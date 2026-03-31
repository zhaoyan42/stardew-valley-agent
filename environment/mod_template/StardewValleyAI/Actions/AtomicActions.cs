using System;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Tools;
using xTile.Dimensions;
using Rectangle = Microsoft.Xna.Framework.Rectangle;

namespace StardewValleyAI.Actions
{
    public static class AtomicActions
    {
        private static IMonitor Monitor;

        public static void Initialize(IMonitor monitor)
        {
            Monitor = monitor;
        }

        /// <summary>
        /// Interact with the object or NPC at the specified tile coordinates.
        /// </summary>
        public static bool Interact(int tileX, int tileY)
        {
            if (!Context.IsWorldReady) return false;

            // Target the center of the tile for better hit rate
            Location tileLocation = new Location(tileX * 64 + 32, tileY * 64 + 32);
            
            // Check if it's an NPC or an object that requires inventory space (like harvesting)
            // Note: Simple harvest via interact usually checks inventory internally, 
            // but we can be proactive if we know it's a crop.
            
            bool interacted = Game1.currentLocation.checkAction(tileLocation, Game1.viewport, Game1.player);

            if (interacted)
            {
                Monitor?.Log($"Interacted with tile ({tileX}, {tileY})", LogLevel.Debug);
            }
            else
            {
                Monitor?.Log($"No interaction found at tile ({tileX}, {tileY})", LogLevel.Debug);
            }

            return interacted;
        }

        /// <summary>
        /// Switch to the specified tool and use it at the target tile.
        /// </summary>
        public static bool UseTool(string toolName, int tileX, int tileY)
        {
            if (!Context.IsWorldReady) return false;

            // Check stamina
            if (Game1.player.stamina <= 0)
            {
                Monitor?.Log("Stamina too low to use tool.", LogLevel.Warn);
                return false;
            }

            // Find tool in inventory
            var tool = Game1.player.Items.OfType<Tool>().FirstOrDefault(t => t.Name.Equals(toolName, StringComparison.OrdinalIgnoreCase));
            if (tool == null)
            {
                Monitor?.Log($"Tool '{toolName}' not found in inventory.", LogLevel.Warn);
                return false;
            }

            // Set current tool
            int toolIndex = Game1.player.Items.IndexOf(tool);
            Game1.player.CurrentToolIndex = toolIndex;

            // Target position: Center of the tile
            Vector2 targetPos = new Vector2(tileX * 64 + 32, tileY * 64 + 32);
            Game1.player.lastClick = targetPos;
            
            // Orientation
            Game1.player.faceGeneralDirection(targetPos);

            // Use tool
            // Note: beginUsing starts the animation. 
            // In a tick-based system, we'd wait for Game1.player.UsingTool to become false.
            tool.beginUsing(Game1.currentLocation, (int)targetPos.X, (int)targetPos.Y, Game1.player);
            
            // Some tools need endUsing immediately if they are non-continuous
            if (!(tool is WateringCan) && !(tool is FishingRod))
            {
                tool.endUsing(Game1.currentLocation, Game1.player);
            }

            Monitor?.Log($"Used {toolName} at ({tileX}, {tileY})", LogLevel.Debug);
            return true;
        }

        /// <summary>
        /// Perform an action with an item (consume, wear, plant, or place) at the target coordinates.
        /// </summary>
        public static bool ItemAction(string itemName, int tileX, int tileY)
        {
            if (!Context.IsWorldReady) return false;

            var item = Game1.player.Items.FirstOrDefault(i => i != null && i.Name.Equals(itemName, StringComparison.OrdinalIgnoreCase));
            if (item == null)
            {
                Monitor?.Log($"Item '{itemName}' not found in inventory.", LogLevel.Warn);
                return false;
            }

            // If it's edible and we want to consume it (special case, usually tileX/Y = -1)
            if (tileX == -1 && item is StardewValley.Object obj && obj.Edibility != -300)
            {
                Game1.player.eatObject(obj);
                Monitor?.Log($"Consumed {itemName}", LogLevel.Debug);
                return true;
            }

            // Set as active item
            int itemIndex = Game1.player.Items.IndexOf(item);
            Game1.player.CurrentToolIndex = itemIndex;

            // Target position
            Vector2 targetPos = new Vector2(tileX * 64 + 32, tileY * 64 + 32);
            
            // Try to place or use item
            if (item is StardewValley.Object actionObj)
            {
                // Planting/Placing logic
                if (Utility.withinRadiusOfPlayer((int)targetPos.X, (int)targetPos.Y, 1, Game1.player))
                {
                    if (actionObj.placementAction(Game1.currentLocation, (int)targetPos.X, (int)targetPos.Y, Game1.player))
                    {
                        Monitor?.Log($"Placed/Planted {itemName} at ({tileX}, {tileY})", LogLevel.Debug);
                        // Inventory management is handled by placementAction
                        return true;
                    }
                }
            }

            Monitor?.Log($"Failed to use/place {itemName} at ({tileX}, {tileY}). Out of range or invalid location.", LogLevel.Warn);
            return false;
        }
    }
}