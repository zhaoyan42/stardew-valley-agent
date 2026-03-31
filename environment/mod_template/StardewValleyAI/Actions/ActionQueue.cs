using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValleyAI.Pathfinding;

namespace StardewValleyAI.Actions
{
    public interface IAction
    {
        string Name { get; }
        bool Execute(); // Returns true if it started successfully
        void Update(); // Called every tick while active
        bool IsComplete(); // Returns true if the action (and its animation) is finished
    }

    public class MoveToAction : IAction
    {
        public string Name => $"MoveTo({TargetX}, {TargetY})";
        public int TargetX;
        public int TargetY;
        private List<Vector2> path;
        private int currentPathIndex = 0;
        private bool failed = false;

        public MoveToAction(int x, int y)
        {
            TargetX = x;
            TargetY = y;
        }

        public bool Execute()
        {
            Vector2 start = Game1.player.getTileLocation();
            Vector2 end = new Vector2(TargetX, TargetY);
            
            if (start == end) return true;

            path = AStar.FindPath(start, end, Game1.currentLocation);
            
            if (path == null || path.Count == 0)
            {
                failed = true;
                return false;
            }
            
            currentPathIndex = 0;
            return true;
        }

        public void Update()
        {
            if (path == null || currentPathIndex >= path.Count) 
            {
                Game1.player.Halt();
                return;
            }

            Vector2 targetTile = path[currentPathIndex];
            Vector2 targetPixel = new Vector2(targetTile.X * 64 + 32, targetTile.Y * 64 + 32);
            Vector2 playerPixel = Game1.player.getStandingPosition();

            float distance = Vector2.Distance(playerPixel, targetPixel);

            if (distance < 16f) // Close enough to current tile center
            {
                currentPathIndex++;
                if (currentPathIndex >= path.Count)
                {
                    Game1.player.Halt();
                    return;
                }
                targetTile = path[currentPathIndex];
                targetPixel = new Vector2(targetTile.X * 64 + 32, targetTile.Y * 64 + 32);
            }

            MoveTowards(targetPixel);
        }

        private void MoveTowards(Vector2 target)
        {
            Vector2 playerPos = Game1.player.getStandingPosition();
            
            Game1.player.SetMovingOnlyUp(playerPos.Y > target.Y + 8);
            Game1.player.SetMovingOnlyDown(playerPos.Y < target.Y - 8);
            Game1.player.SetMovingOnlyLeft(playerPos.X > target.X + 8);
            Game1.player.SetMovingOnlyRight(playerPos.X < target.X - 8);

            // If we are stuck (not moving but supposed to be), we might need to recalculate or just fail
            // For now, simple movement.
        }

        public bool IsComplete()
        {
            if (failed) return true;
            if (path == null || path.Count == 0) return true;
            return currentPathIndex >= path.Count;
        }
    }

    public class ToolAction : IAction
    {
        public string Name => $"UseTool({ToolName}, {TileX}, {TileY})";
        public string ToolName;
        public int TileX;
        public int TileY;
        private bool started = false;

        public ToolAction(string toolName, int x, int y)
        {
            ToolName = toolName;
            TileX = x;
            TileY = y;
        }

        public bool Execute()
        {
            started = AtomicActions.UseTool(ToolName, TileX, TileY);
            return started;
        }

        public void Update() { }

        public bool IsComplete()
        {
            // Tool use is complete when the player is no longer using a tool
            return started && !Game1.player.UsingTool;
        }
    }

    public class InteractAction : IAction
    {
        public string Name => $"Interact({TileX}, {TileY})";
        public int TileX;
        public int TileY;
        private bool done = false;

        public InteractAction(int x, int y)
        {
            TileX = x;
            TileY = y;
        }

        public bool Execute()
        {
            done = AtomicActions.Interact(TileX, TileY);
            return done;
        }

        public void Update() { }

        public bool IsComplete() => done;
    }

    public class ItemUseAction : IAction
    {
        public string Name => $"ItemAction({ItemName}, {TileX}, {TileY})";
        public string ItemName;
        public int TileX;
        public int TileY;
        private bool done = false;

        public ItemUseAction(string itemName, int x, int y)
        {
            ItemName = itemName;
            TileX = x;
            TileY = y;
        }

        public bool Execute()
        {
            done = AtomicActions.ItemAction(ItemName, TileX, TileY);
            return done;
        }

        public void Update() { }

        public bool IsComplete() => done;
    }

    public static class ActionQueue
    {
        private static Queue<IAction> queue = new Queue<IAction>();
        private static IAction currentAction = null;
        private static IMonitor Monitor;
        private static int pauseTicks = 0;

        public static void Initialize(IMonitor monitor)
        {
            Monitor = monitor;
        }

        public static void Enqueue(IAction action)
        {
            queue.Enqueue(action);
        }

        public static void Update()
        {
            if (pauseTicks > 0)
            {
                pauseTicks--;
                return;
            }

            if (currentAction == null)
            {
                if (queue.Count > 0)
                {
                    currentAction = queue.Dequeue();
                    Monitor?.Log($"[ActionQueue] Starting: {currentAction.Name}", LogLevel.Debug);
                    if (!currentAction.Execute())
                    {
                        Monitor?.Log($"[ActionQueue] Action {currentAction.Name} failed to start.", LogLevel.Warn);
                        currentAction = null;
                        // Add a small pause after failure to prevent spamming
                        pauseTicks = 10;
                    }
                }
            }
            else
            {
                currentAction.Update();
                if (currentAction.IsComplete())
                {
                    Monitor?.Log($"[ActionQueue] Finished: {currentAction.Name}", LogLevel.Debug);
                    currentAction = null;
                    // Add a small pause between actions for stability
                    pauseTicks = 5;
                }
            }
        }
        
        public static bool IsEmpty => currentAction == null && queue.Count == 0;
        
        public static void Clear()
        {
            queue.Clear();
            currentAction = null;
            pauseTicks = 0;
        }
    }
}
