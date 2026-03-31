using System;
using System.IO;
using System.Threading.Tasks;
using Newtonsoft.Json;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Menus;
using StardewAIAgent.Communication;
using StardewAIAgent.Models;
using StardewValleyAI.Actions;
using StardewValleyAI.Tactics;

namespace StardewAIAgent
{
    public class ModEntry : Mod
    {
        private McpClient _mcpClient;

        public override void Entry(IModHelper helper)
        {
            _mcpClient = new McpClient("http://localhost:5000"); // Default URL
            
            // Initialize Action Libraries
            AtomicActions.Initialize(this.Monitor);
            TacticalCombos.Initialize(this.Monitor);
            ActionQueue.Initialize(this.Monitor);
            DecisionTable.Initialize(this.Monitor, this.Helper.DirectoryPath);
            
            this.Monitor.Log("Stardew AI Agent initialized.", LogLevel.Debug);

            helper.Events.Input.ButtonPressed += OnButtonPressed;
            helper.Events.GameLoop.UpdateTicked += OnUpdateTicked;
            
            // Register Debug Commands
            helper.ConsoleCommands.Add("ai_screenshot", "Takes a screenshot of the game.", (s, args) => TakeScreenshot());
            helper.ConsoleCommands.Add("ai_export_status", "Exports the player's status as JSON.", (s, args) => ExportStatus());
            helper.ConsoleCommands.Add("ai_request_decision", "Pauses the game and requests a decision from the server.", (s, args) => RequestDecision());
            
            // New Test Commands for Tactical Actions
            helper.ConsoleCommands.Add("ai_clear_farm", "Clears a 10x10 area on the farm.", (s, args) => 
            {
                if (Context.IsWorldReady) 
                    TacticalCombos.ClearArea(new Microsoft.Xna.Framework.Rectangle((int)Game1.player.getTileX(), (int)Game1.player.getTileY(), 10, 10));
            });
        }

        private void OnButtonPressed(object sender, ButtonPressedEventArgs e)
        {
            if (!Context.IsWorldReady) return;

            // Optional: Trigger actions on specific keys for debugging
        }

        private void OnUpdateTicked(object sender, UpdateTickedEventArgs e)
        {
            if (!Context.IsWorldReady) return;

            ActionQueue.Update();
            DecisionTable.Update();
        }

        /// <summary>
        /// Captures a screenshot and saves it to the mod directory.
        /// </summary>
        private void TakeScreenshot()
        {
            string fileName = $"screenshot_{DateTime.Now:yyyyMMdd_HHmmss}.png";
            string filePath = Path.Combine(this.Helper.DirectoryPath, fileName);
            
            // SMAPI doesn't have a direct "TakeScreenshot" that returns a path easily in standard API 
            // but we can use Game1.game1.TakeScreenshot()
            // However, Game1.game1.TakeScreenshot() saves to the 'Screenshots' folder in Stardew Valley app data.
            // If we want a specific path, we might need to handle it differently.
            // For now, let's use the standard way and log where it went.
            
            try 
            {
                Game1.game1.TakeScreenshot(null, null, null, null, null);
                this.Monitor.Log($"Screenshot requested. Check your StardewValley/Screenshots folder.", LogLevel.Info);
            }
            catch (Exception ex)
            {
                this.Monitor.Log($"Failed to take screenshot: {ex.Message}", LogLevel.Error);
            }
        }

        /// <summary>
        /// Exports player status to JSON and logs it.
        /// </summary>
        private void ExportStatus()
        {
            var status = PlayerStatus.Capture();
            if (status == null)
            {
                this.Monitor.Log("Player status not available.", LogLevel.Warn);
                return;
            }

            string json = JsonConvert.SerializeObject(status, Formatting.Indented);
            this.Monitor.Log($"Player Status:\n{json}", LogLevel.Info);
            
            // Also save to a file for external tools to read
            File.WriteAllText(Path.Combine(this.Helper.DirectoryPath, "status.json"), json);
        }

        /// <summary>
        /// Pauses the game by opening a dialogue box and requests a decision.
        /// </summary>
        private async void RequestDecision()
        {
            if (Game1.activeClickableMenu != null)
            {
                this.Monitor.Log("Cannot request decision while another menu is open.", LogLevel.Warn);
                return;
            }

            // Pause the game by opening a dialogue box
            Game1.activeClickableMenu = new DialogueBox("AI Agent is making a decision...");
            this.Monitor.Log("Game paused. Requesting decision from server...", LogLevel.Info);

            var status = PlayerStatus.Capture();
            string response = await _mcpClient.SendStateAsync(status);
            
            this.Monitor.Log($"Server Response: {response}", LogLevel.Info);

            // Close the dialogue box once the decision is received (or after a timeout)
            // Note: In a real scenario, you'd want to handle the decision here.
            // For now, we'll just close it after a short delay to simulate.
            await Task.Delay(2000);
            Game1.exitActiveMenu();
            this.Monitor.Log("Game resumed.", LogLevel.Info);
        }
    }
}