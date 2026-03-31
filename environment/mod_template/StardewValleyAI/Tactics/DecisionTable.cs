using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Xna.Framework;
using Newtonsoft.Json;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Monsters;
using StardewValleyAI.Actions;

namespace StardewValleyAI.Tactics
{
    public class TacticsConfig
    {
        public float kiting_distance { get; set; } = 2.5f;
        public int heal_threshold { get; set; } = 30;
        public string heal_item_name { get; set; } = "Common Mushroom";
    }

    public static class DecisionTable
    {
        private static IMonitor Monitor;
        private static TacticsConfig Config;
        private static string ConfigPath;
        private static int combatCooldown = 0;

        public static void Initialize(IMonitor monitor, string modPath)
        {
            Monitor = monitor;
            ConfigPath = Path.Combine(modPath, "tactics.json");
            LoadConfig();
        }

        public static void LoadConfig()
        {
            if (File.Exists(ConfigPath))
            {
                try
                {
                    string json = File.ReadAllText(ConfigPath);
                    Config = JsonConvert.DeserializeObject<TacticsConfig>(json);
                    Monitor.Log("Tactics config loaded.", LogLevel.Debug);
                }
                catch (Exception ex)
                {
                    Monitor.Log($"Failed to load tactics config: {ex.Message}", LogLevel.Error);
                    Config = new TacticsConfig();
                }
            }
            else
            {
                Config = new TacticsConfig();
                SaveConfig();
            }
        }

        public static void SaveConfig()
        {
            try
            {
                string json = JsonConvert.SerializeObject(Config, Formatting.Indented);
                File.WriteAllText(ConfigPath, json);
            }
            catch (Exception ex)
            {
                Monitor.Log($"Failed to save tactics config: {ex.Message}", LogLevel.Error);
            }
        }

        public static void Update()
        {
            if (!Context.IsWorldReady || Game1.currentLocation == null) return;

            if (combatCooldown > 0)
            {
                combatCooldown--;
            }

            // 1. Emergency Healing
            if (Game1.player.health <= Config.heal_threshold)
            {
                if (ActionQueue.IsEmpty)
                {
                    var healItem = Game1.player.Items.FirstOrDefault(i => i != null && i.Name.Equals(Config.heal_item_name, StringComparison.OrdinalIgnoreCase));
                    if (healItem != null)
                    {
                        Monitor.Log($"Low health ({Game1.player.health})! Using {Config.heal_item_name}.", LogLevel.Warn);
                        ActionQueue.Enqueue(new ItemUseAction(Config.heal_item_name, -1, -1));
                        return;
                    }
                }
            }

            // 2. Auto Combat
            if (ActionQueue.IsEmpty && combatCooldown <= 0)
            {
                var monsters = Game1.currentLocation.characters.OfType<Monster>().ToList();
                if (monsters.Count > 0)
                {
                    Monster nearestMonster = null;
                    float minDistance = float.MaxValue;

                    foreach (var monster in monsters)
                    {
                        float dist = Vector2.Distance(Game1.player.getTileLocation(), monster.getTileLocation());
                        if (dist < minDistance)
                        {
                            minDistance = dist;
                            nearestMonster = monster;
                        }
                    }

                    if (nearestMonster != null && minDistance < 15f) // Only care about monsters within 15 tiles
                    {
                        ManageCombat(nearestMonster, minDistance);
                    }
                }
            }
        }

        private static void ManageCombat(Monster monster, float distance)
        {
            // Kiting logic
            if (distance < Config.kiting_distance)
            {
                // Move away from monster
                Vector2 playerTile = Game1.player.getTileLocation();
                Vector2 monsterTile = monster.getTileLocation();
                Vector2 diff = playerTile - monsterTile;
                if (diff == Vector2.Zero) diff = new Vector2(1, 0);
                diff.Normalize();
                
                Vector2 escapeTile = playerTile + diff * 3f; // Move 3 tiles away
                
                Monitor.Log($"Monster {monster.Name} too close ({distance:F1})! Kiting to {(int)escapeTile.X}, {(int)escapeTile.Y}", LogLevel.Debug);
                ActionQueue.Enqueue(new MoveToAction((int)escapeTile.X, (int)escapeTile.Y));
                combatCooldown = 20; // Short cooldown after kiting command
            }
            else if (distance <= 2.0f) // Close enough to attack (increased slightly for better hit)
            {
                // Attack
                Monitor.Log($"Attacking {monster.Name} at distance {distance:F1}!", LogLevel.Debug);
                string weaponName = Game1.player.CurrentTool?.Name ?? "Sword";
                ActionQueue.Enqueue(new ToolAction(weaponName, (int)monster.getTileX(), (int)monster.getTileY()));
                combatCooldown = 30; // Cooldown after attack to allow animation
            }
            else if (distance < 10f)
            {
                // Move towards monster to attack
                Monitor.Log($"Approaching {monster.Name} ({distance:F1} tiles away)...", LogLevel.Debug);
                ActionQueue.Enqueue(new MoveToAction((int)monster.getTileX(), (int)monster.getTileY()));
                combatCooldown = 40; // Cooldown for movement
            }
        }
    }
}
