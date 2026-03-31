using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewValley;
using xTile.Dimensions;
using Rectangle = Microsoft.Xna.Framework.Rectangle;

namespace StardewValleyAI.Pathfinding
{
    public class Node
    {
        public int X;
        public int Y;
        public int G; // Cost from start
        public int H; // Heuristic (Manhattan distance to goal)
        public int F => G + H;
        public Node Parent;

        public Node(int x, int y)
        {
            X = x;
            Y = y;
        }
    }

    public static class AStar
    {
        public static List<Vector2> FindPath(Vector2 start, Vector2 end, GameLocation location)
        {
            int startX = (int)start.X;
            int startY = (int)start.Y;
            int endX = (int)end.X;
            int endY = (int)end.Y;

            if (startX == endX && startY == endY) return new List<Vector2>();

            var openSet = new List<Node>();
            var closedSet = new HashSet<string>();

            Node startNode = new Node(startX, startY);
            startNode.H = Math.Abs(startX - endX) + Math.Abs(startY - endY);
            openSet.Add(startNode);

            // Limit search to prevent infinite loops or long hangs
            int maxIterations = 2000;
            int iterations = 0;

            while (openSet.Count > 0 && iterations < maxIterations)
            {
                iterations++;
                // Get node with lowest F cost
                Node current = openSet.OrderBy(n => n.F).ThenBy(n => n.H).First();

                if (current.X == endX && current.Y == endY)
                {
                    return RetracePath(current);
                }

                openSet.Remove(current);
                closedSet.Add($"{current.X},{current.Y}");

                foreach (var neighbor in GetNeighbors(current, location))
                {
                    if (closedSet.Contains($"{neighbor.X},{neighbor.Y}")) continue;

                    int newCostToNeighbor = current.G + 1;
                    var existingNode = openSet.FirstOrDefault(n => n.X == neighbor.X && n.Y == neighbor.Y);

                    if (existingNode == null || newCostToNeighbor < existingNode.G)
                    {
                        neighbor.G = newCostToNeighbor;
                        neighbor.H = Math.Abs(neighbor.X - endX) + Math.Abs(neighbor.Y - endY);
                        neighbor.Parent = current;

                        if (existingNode == null)
                        {
                            openSet.Add(neighbor);
                        }
                    }
                }
            }

            return null; // No path found
        }

        private static List<Vector2> RetracePath(Node endNode)
        {
            var path = new List<Vector2>();
            Node current = endNode;
            while (current != null)
            {
                path.Add(new Vector2(current.X, current.Y));
                current = current.Parent;
            }
            path.Reverse();
            return path;
        }

        private static List<Node> GetNeighbors(Node node, GameLocation location)
        {
            var neighbors = new List<Node>();
            int[] dx = { 0, 0, 1, -1 };
            int[] dy = { 1, -1, 0, 0 };

            for (int i = 0; i < 4; i++)
            {
                int nx = node.X + dx[i];
                int ny = node.Y + dy[i];

                if (IsWalkable(nx, ny, location))
                {
                    neighbors.Add(new Node(nx, ny));
                }
            }
            return neighbors;
        }

        public static bool IsWalkable(int x, int y, GameLocation location)
        {
            // Boundary checks
            if (x < 0 || y < 0 || x >= location.map.Layers[0].LayerWidth || y >= location.map.Layers[0].LayerHeight)
                return false;

            // Basic passability check
            var tileLocation = new Location(x * 64, y * 64);
            
            // Check if the tile is passable by the player
            if (!location.isTilePassable(tileLocation, Game1.viewport)) return false;

            // Check for objects that block movement (using Rectangle for precision)
            Rectangle tileRect = new Rectangle(x * 64, y * 64, 64, 64);
            
            // isCollidingPosition check (more thorough but more expensive)
            // We shrink the player box slightly to be more forgiving in pathfinding
            Rectangle playerBox = new Rectangle(x * 64 + 8, y * 64 + 8, 48, 48);
            if (location.isCollidingPosition(playerBox, Game1.viewport, true, 0, false, Game1.player))
                return false;

            return true;
        }
    }
}
