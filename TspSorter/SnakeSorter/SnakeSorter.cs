using System;
using System.Collections.Generic;

namespace SorterLib
{
    /// <summary>
    /// 蛇形路径排序器：
    /// 按 y 自适应分行 → 逐行就近选方向（蛇形）→ 2-opt 优化。
    /// 输入输出均为 double[n, 2]，每行一个点 [x, y]。
    /// </summary>
    public static class SnakeSorter
    {
        // ================= 公开接口 =================

        /// <summary>
        /// 简化接口：只返回排序后的点集。
        /// </summary>
        public static double[,] Sort(double[,] inPoints)
        {
            double[,] result;
            double before, after;
            if (!Sort(inPoints, out result, out before, out after))
                return null;
            return result;
        }

        /// <summary>
        /// 完整接口：返回排序点集 + 优化前后长度。
        /// </summary>
        public static bool Sort(
            double[,] inPoints,
            out double[,] outPoints,
            out double beforeLength,
            out double afterLength)
        {
            outPoints = null;
            beforeLength = 0;
            afterLength = 0;

            if (inPoints == null)
            {
                Console.WriteLine("[C# Snake] inPoints is null");
                return false;
            }

            int n = inPoints.GetLength(0);
            Console.WriteLine($"[C# Snake] Sort called, n={n}");

            for (int i = 0; i < n; i++)
                Console.WriteLine($"[C# Snake] in[{i}] = ({inPoints[i, 0]}, {inPoints[i, 1]})");

            if (n < 2)
            {
                outPoints = ClonePoints(inPoints);
                Console.WriteLine("[C# Snake] n<2, return clone");
                return true;
            }

            // 1. 转点列表
            var pts = new List<PointD>(n);
            for (int i = 0; i < n; i++)
                pts.Add(new PointD(inPoints[i, 0], inPoints[i, 1]));

            // 2. 分行
            var rows = SplitRows(pts, 1.5);
            Console.WriteLine($"[C# Snake] split into {rows.Count} rows");

            // 3. 行方向就近选择（蛇形）
            var path = ChooseRowDirection(rows);
            beforeLength = PathLength(path);
            Console.WriteLine($"[C# Snake] before 2-opt length = {beforeLength:F2}");

            // 4. 2-opt
            path = TwoOpt(path);
            afterLength = PathLength(path);
            Console.WriteLine($"[C# Snake] after 2-opt length = {afterLength:F2}");

            // 5. 输出
            outPoints = new double[n, 2];
            for (int i = 0; i < n; i++)
            {
                outPoints[i, 0] = path[i].X;
                outPoints[i, 1] = path[i].Y;
                Console.WriteLine($"[C# Snake] out[{i}] = ({path[i].X}, {path[i].Y})");
            }

            Console.WriteLine("[C# Snake] Sort done");
            return true;
        }

        // ================= 内部结构 =================

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

        // ================= 分行 =================

        private static List<List<PointD>> SplitRows(List<PointD> points, double gapFactor)
        {
            var rows = new List<List<PointD>>();
            if (points == null || points.Count == 0)
                return rows;

            // 按 y 排序
            var pts = new List<PointD>(points);
            pts.Sort((a, b) => a.Y.CompareTo(b.Y));

            var ys = new List<double>(pts.Count);
            for (int i = 0; i < pts.Count; i++)
                ys.Add(pts[i].Y);

            var gaps = new List<double>();
            for (int i = 0; i < ys.Count - 1; i++)
            {
                double g = ys[i + 1] - ys[i];
                if (g > 1e-9)
                    gaps.Add(g);
            }

            if (gaps.Count == 0)
            {
                rows.Add(pts);
                return rows;
            }

            gaps.Sort();
            double med = gaps[gaps.Count / 2];
            double threshold = Math.Max(med * gapFactor, 5.0);

            var current = new List<PointD> { pts[0] };
            rows.Add(current);

            for (int i = 1; i < pts.Count; i++)
            {
                if (ys[i] - ys[i - 1] > threshold)
                {
                    current = new List<PointD> { pts[i] };
                    rows.Add(current);
                }
                else
                {
                    current.Add(pts[i]);
                }
            }
            return rows;
        }

        // ================= 行方向就近选择 =================

        private static List<PointD> ChooseRowDirection(List<List<PointD>> rows)
        {
            var result = new List<PointD>();
            if (rows == null || rows.Count == 0)
                return result;

            // 第一行：左 -> 右
            var first = new List<PointD>(rows[0]);
            first.Sort((a, b) => a.X.CompareTo(b.X));
            result.AddRange(first);
            PointD tail = first[first.Count - 1];

            for (int r = 1; r < rows.Count; r++)
            {
                var lr = new List<PointD>(rows[r]);
                lr.Sort((a, b) => a.X.CompareTo(b.X));

                var rl = new List<PointD>(lr);
                rl.Reverse();

                double d1 = Dist(tail, lr[0]);
                double d2 = Dist(tail, rl[0]);

                var chosen = (d1 <= d2) ? lr : rl;
                result.AddRange(chosen);
                tail = chosen[chosen.Count - 1];
            }
            return result;
        }

        // ================= 2-opt =================

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