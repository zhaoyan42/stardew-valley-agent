using System;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace StardewAIAgent
{
    public class ModEntry : Mod
    {
        public override void Entry(IModHelper helper)
        {
            this.Monitor.Log("Stardew AI Agent initialized.", LogLevel.Debug);
        }
    }
}