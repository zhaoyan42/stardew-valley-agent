using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.TerrainFeatures;
using StardewValley.Tools;
using StardewValley.Menus;
using Rectangle = Microsoft.Xna.Framework.Rectangle;

namespace StardewValleyAI.Actions
{
    public static class TacticalCombos
    {
        private static IMonitor Monitor;

        public static void Initialize(IMonitor monitor)
        {
            Monitor = monitor;
        }

        /// <summary>
        /// Automatically clear an area of weeds, stones, and twigs.
        /// </summary>
        public static void ClearArea(Rectangle rect)
        {
            if (!Context.IsWorldReady) return;

            Monitor?.Log($"Queueing area clearing for {rect}", LogLevel.Info);

            for (int x = rect.X; x < rect.X + rect.Width; x++)
            {
                for (int y = rect.Y; y < rect.Y + rect.Height; y++)
                {
                    Vector2 tile = new Vector2(x, y);
                    
                    // Check for weeds/debris on current location
                    if (Game1.currentLocation.objects.TryGetValue(tile, out StardewValley.Object obj))
                    {
                        if (obj.Name.Contains("Weeds"))
                        {
                            ActionQueue.Enqueue(new ToolAction("Scythe", x, y));
                        }
                        else if (obj.Name.Contains("Stone"))
                        {
                            ActionQueue.Enqueue(new ToolAction("Pickaxe", x, y));
                        }
                        else if (obj.Name.Contains("Twig"))
                        {
                            ActionQueue.Enqueue(new ToolAction("Axe", x, y));
                        }
                    }
                    
                    // Check for logs/stumps
                    if (Game1.currentLocation.resourceClumps.Any(c => c.Tile == tile))
                    {
                        ActionQueue.Enqueue(new ToolAction("Axe", x, y));
                    }
                }
            }
        }

        /// <summary>
        /// Automatically water and harvest crops in an area.
        /// </summary>
        public static void TendCrops(Rectangle rect)
        {
            if (!Context.IsWorldReady) return;

            Monitor?.Log($"Queueing crop tending for {rect}", LogLevel.Info);

            for (int x = rect.X; x < rect.X + rect.Width; x++)
            {
                for (int y = rect.Y; y < rect.Y + rect.Height; y++)
                {
                    Vector2 tile = new Vector2(x, y);
                    
                    if (Game1.currentLocation.terrainFeatures.TryGetValue(tile, out TerrainFeature feature) && feature is HoeDirt dirt)
                    {
                        // Harvest if ready
                        if (dirt.crop != null && dirt.crop.currentPhase.Value >= dirt.crop.phaseDays.Count - 1)
                        {
                            // Check inventory space before harvesting
                            if (Game1.player.freeSpotsInInventory() <= 0)
                            {
                                Monitor?.Log("Inventory full, skipping harvest.", LogLevel.Warn);
                            }
                            else
                            {
                                ActionQueue.Enqueue(new InteractAction(x, y));
                            }
                        }

                        // Water if not watered
                        if (dirt.state.Value != HoeDirt.watered)
                        {
                            ActionQueue.Enqueue(new ToolAction("Watering Can", x, y));
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Navigate to a shop NPC and buy specified items.
        /// </summary>
        public static void ShopSequence(string npcName, List<string> items)
        {
            if (!Context.IsWorldReady) return;

            ActionQueue.Enqueue(new ShopAction(npcName, items, Monitor));
        }
    }

    public class ShopAction : IAction
    {
        public string Name => $"ShopSequence({NpcName})";
        public string NpcName;
        public List<string> ItemNames;
        private IMonitor Monitor;
        private bool started = false;
        private bool finished = false;
        private int timeoutTicks = 100; // 100 ticks timeout to open shop

        public ShopAction(string npcName, List<string> items, IMonitor monitor)
        {
            NpcName = npcName;
            ItemNames = items;
            Monitor = monitor;
        }

        public bool Execute()
        {
            NPC shopNPC = Game1.currentLocation.getCharacterFromName(NpcName);
            if (shopNPC == null) return false;

            Monitor.Log($"Attempting to open shop with {NpcName}", LogLevel.Debug);
            AtomicActions.Interact((int)shopNPC.getTileX(), (int)shopNPC.getTileY());
            started = true;
            return true;
        }

        public bool IsComplete()
        {
            if (!started) return false;
            if (finished) return true;

            if (Game1.activeClickableMenu is ShopMenu shopMenu)
            {
                foreach (var itemName in ItemNames)
                {
                    var itemToBuy = shopMenu.itemPriceAndStock.Keys.FirstOrDefault(i => i.Name.Equals(itemName, StringComparison.OrdinalIgnoreCase));
                    if (itemToBuy != null)
                    {
                        if (Game1.player.freeSpotsInInventory() <= 0)
                        {
                            Monitor.Log($"Inventory full, cannot buy {itemName}.", LogLevel.Warn);
                            continue;
                        }

                        int price = shopMenu.itemPriceAndStock[itemToBuy][0];
                        if (Game1.player.Money < price)
                        {
                            Monitor.Log($"Not enough money for {itemName}.", LogLevel.Warn);
                            continue;
                        }

                        // Use the internal purchase method via reflection or just simulate the click
                        // Since we are already in the menu, we can try to find the component
                        var component = shopMenu.forSaleButtons.FirstOrDefault(b => b.name == itemToBuy.Name || (shopMenu.forSale.Count > shopMenu.forSaleButtons.IndexOf(b) && shopMenu.forSale[shopMenu.forSaleButtons.IndexOf(b)].Name == itemToBuy.Name));
                        
                        if (component != null)
                        {
                            Monitor.Log($"Buying {itemName}...", LogLevel.Info);
                            shopMenu.receiveLeftClick(component.bounds.Center.X, component.bounds.Center.Y);
                        }
                    }
                }
                finished = true;
                Game1.exitActiveMenu();
                return true;
            }

            timeoutTicks--;
            if (timeoutTicks <= 0)
            {
                Monitor.Log("Timed out waiting for ShopMenu to open.", LogLevel.Warn);
                return true; // End action
            }

            return false;
        }
    }
}