using System;
using System.Collections.Generic;

namespace SorterLib
{
    public static class TspSorter
    {
        public static double[,] Sort(double[,] inPoints)
        {
            double[,] result;
            double a, b;
            if (!Sort(inPoints, out result, out a, out b))
                return null;
            return result;
        }

        public static bool Sort(
            double[,] inPoints,
            out double[,] outPoints,
            out double initialLength,
            out double optimizedLength)
        {
            outPoints = null;
            initialLength = 0;
            optimizedLength = 0;

            if (inPoints == null)
            {
                Console.WriteLine("[C#] inPoints is null");
                return false;
            }

            int n = inPoints.GetLength(0);
            Console.WriteLine($"[C#] Sort called, n={n}");

            for (int i = 0; i < n; i++)
                Console.WriteLine($"[C#] in[{i}] = ({inPoints[i, 0]}, {inPoints[i, 1]})");

            if (n < 2)
            {
                outPoints = ClonePoints(inPoints);
                Console.WriteLine("[C#] n<2, return clone");
                return true;
            }

            var pts = new List<PointD>(n);
            for (int i = 0; i < n; i++)
                pts.Add(new PointD(inPoints[i, 0], inPoints[i, 1]));

            var path = NearestNeighbor(pts);
            initialLength = PathLength(path);
            Console.WriteLine($"[C#] initial length = {initialLength:F2}");

            path = TwoOpt(path);
            optimizedLength = PathLength(path);
            Console.WriteLine($"[C#] optimized length = {optimizedLength:F2}");

            outPoints = new double[n, 2];
            for (int i = 0; i < n; i++)
            {
                outPoints[i, 0] = path[i].X;
                outPoints[i, 1] = path[i].Y;
                Console.WriteLine($"[C#] out[{i}] = ({path[i].X}, {path[i].Y})");
            }

            Console.WriteLine("[C#] Sort done");
            return true;
        }

        private struct PointD
        {
            public double X;
            public double Y;
            public PointD(double x, double y) { X = x; Y = y; }
        }

        private static double Dist(PointD a, PointD b)
        {
            double dx = a.X - b.X;
            double dy = a.Y - b.Y;
            return Math.Sqrt(dx * dx + dy * dy);
        }

        private static double PathLength(List<PointD> path)
        {
            if (path == null || path.Count < 2) return 0;
            double total = 0;
            for (int i = 0; i < path.Count - 1; i++)
                total += Dist(path[i], path[i + 1]);
            return total;
        }

        private static List<PointD> NearestNeighbor(List<PointD> points)
        {
            int n = points.Count;
            var unused = new List<PointD>(points);
            var path = new List<PointD>(n);
            PointD current = unused[0];
            path.Add(current);
            unused.RemoveAt(0);

            while (unused.Count > 0)
            {
                int bestIdx = 0;
                double bestD = double.MaxValue;
                for (int i = 0; i < unused.Count; i++)
                {
                    double d = Dist(current, unused[i]);
                    if (d < bestD) { bestD = d; bestIdx = i; }
                }
                current = unused[bestIdx];
                path.Add(current);
                unused.RemoveAt(bestIdx);
            }
            return path;
        }

        private static List<PointD> TwoOpt(List<PointD> path)
        {
            int n = path.Count;
            if (n < 4) return path;

            bool improved = true;
            while (improved)
            {
                improved = false;
                for (int i = 0; i < n - 3; i++)
                {
                    for (int j = i + 2; j < n - 1; j++)
                    {
                        double oldD = Dist(path[i], path[i + 1]) + Dist(path[j], path[j + 1]);
                        double newD = Dist(path[i], path[j]) + Dist(path[i + 1], path[j + 1]);
                        if (newD < oldD - 1e-12)
                        {
                            Reverse(path, i + 1, j);
                            improved = true;
                        }
                    }
                }
            }
            return path;
        }

        private static void Reverse(List<PointD> list, int start, int end)
        {
            while (start < end)
            {
                PointD tmp = list[start];
                list[start] = list[end];
                list[end] = tmp;
                start++; end--;
            }
        }

        private static double[,] ClonePoints(double[,] src)
        {
            int n = src.GetLength(0);
            var dst = new double[n, 2];
            for (int i = 0; i < n; i++)
            {
                dst[i, 0] = src[i, 0];
                dst[i, 1] = src[i, 1];
            }
            return dst;
        }
    }
}