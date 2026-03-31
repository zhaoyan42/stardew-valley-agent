using System;
using StardewValley;

namespace StardewAIAgent.Models
{
    public class PlayerStatus
    {
        public string Name { get; set; }
        public int Money { get; set; }
        public float Stamina { get; set; }
        public int Health { get; set; }
        public string Location { get; set; }
        public float X { get; set; }
        public float Y { get; set; }
        public int TimeOfDay { get; set; }
        public string Season { get; set; }
        public int DayOfMonth { get; set; }
        public int Year { get; set; }

        public static PlayerStatus Capture()
        {
            if (Game1.player == null) return null;

            return new PlayerStatus
            {
                Name = Game1.player.Name,
                Money = Game1.player.Money,
                Stamina = Game1.player.stamina,
                Health = Game1.player.health,
                Location = Game1.currentLocation?.Name,
                X = Game1.player.Position.X,
                Y = Game1.player.Position.Y,
                TimeOfDay = Game1.timeOfDay,
                Season = Game1.currentSeason,
                DayOfMonth = Game1.dayOfMonth,
                Year = Game1.year
            };
        }
    }
}