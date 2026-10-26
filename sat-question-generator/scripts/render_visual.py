#!/usr/bin/env python3
"""
Renders a structured visual_data spec into SVG markup for SAT Math questions that need
a graph, geometric figure, or scatterplot. Tables don't go through this script -- they're
plain structured data (headers/rows) that the frontend renders directly as an HTML table.

Why this exists: an LLM describing "draw a line with slope 2" in prose and an LLM trying to
literally draw pixel-accurate figures are both unreliable. This script takes precise,
unambiguous numeric parameters (which an LLM IS reliably good at producing) and renders
them deterministically with matplotlib, so the visual always exactly matches the math.

Usage:
    python render_visual.py <spec.json> <output.svg>

Spec format (visual_type "graph"):
{
  "visual_type": "graph",
  "visual_data": {
    "chart_type": "function" | "scatter" | "bar" | "inequality",
    "x_label": "x", "y_label": "y",
    "x_range": [-10, 10], "y_range": [-10, 10],   // omit for bar charts
    "title": "optional title",

    // OPTIONAL, any chart_type except bar -- force gridline/tick spacing.
    // USE THESE on any question where the student must READ A VALUE OFF THE GRAPH.
    // Matplotlib otherwise picks tick spacing from the range, which can leave the queried
    // point sitting between labeled gridlines and make the item unanswerable as intended.
    // Set these so every point the student must read lands exactly on a labeled tick.
    "x_tick_step": 1,
    "y_tick_step": 2,

    // OPTIONAL, any chart_type except bar -- draw and label specific points.
    "mark_points": [{"point": [3, 2], "label": "A"}, {"point": [0, -3]}],

    // chart_type == "function": ONE function
    "function": {"kind": "linear", "params": {"m": 2, "b": -3}}
      // kind "linear": params m, b -> y = m*x + b
      // kind "quadratic": params a, b, c -> y = a*x^2 + b*x + c
      // kind "absolute_value": params a, h, k -> y = a*|x - h| + k
      // kind "exponential": params a, b -> y = a * b^x
      // kind "cubic": params a, b, c, d -> y = a*x^3 + b*x^2 + c*x + d  (added run 22)

    // chart_type == "function": TWO OR MORE functions on one grid (e.g. a system of two
    // linear equations, where the answer is the intersection point). Use "functions"
    // INSTEAD OF "function" -- don't supply both. Each entry takes the same kind/params
    // as above, plus an optional "label" which turns on a legend.
    "functions": [
      {"kind": "linear", "params": {"m": 2, "b": 1},  "label": "y = 2x + 1"},
      {"kind": "linear", "params": {"m": -1, "b": 7}, "label": "y = -x + 7"}
    ],

    // chart_type == "inequality": one or more shaded half-planes. Each boundary is drawn
    // SOLID for <= and >=, DASHED for < and > (the standard convention, and often the
    // thing the question is actually testing). "operator" is required.
    // Boundaries use the same kind/params as functions, so a boundary can be nonlinear too.
    "inequalities": [
      {"kind": "linear", "params": {"m": 3, "b": -8},  "operator": ">"},
      {"kind": "linear", "params": {"m": -1, "b": 6},  "operator": "<="}
    ],
    // With two or more inequalities, set this true to shade ONLY the region satisfying all
    // of them (what a real system-of-inequalities figure shows). Leave false/absent to
    // shade each half-plane separately, with the overlap appearing darker.
    "shade_intersection": true,

    // chart_type == "scatter":
    "points": [[1, 2], [2, 4.1], [3, 5.9]],
    "best_fit_line": {"m": 2, "b": 0.1}   // optional

    // chart_type == "bar":
    "categories": ["A", "B", "C"],
    "values": [5, 8, 3]
  }
}

Spec format (visual_type "geometry"):
{
  "visual_type": "geometry",
  "visual_data": {
    "shape": "triangle" | "right_triangle" | "circle" | "rectangle",

    // right_triangle: side_lengths = [leg1, leg2, hypotenuse], in that exact order.
    // The right angle is ALWAYS at vertex 0 -- so if you provide angle_labels, put "90°" (or whatever
    // label) at index 0, not wherever seems visually intuitive.
    // triangle (non-right): side_lengths = [a, b, c] using standard notation where side a is opposite
    // vertex 0, side b is opposite vertex 1, side c is opposite vertex 2.
    "side_lengths": [3, 4, 5],
    "side_labels": ["3", "4", "5"],       // same order/index as side_lengths; can differ from the actual
                                            // numeric length (e.g. "x") when the length is the unknown being solved for
    "angle_labels": ["90°", "", ""], // optional, index i labels the angle at vertex i. For right_triangle
                                            // this MUST be index 0 if you want the right-angle mark to appear
                                            // in the correct place -- this is a common mistake, double check it.

    // circle:
    "radius": 5,
    "radius_label": "5",
    // optional (run 79): "center_label": "O",
    //   "points": [{"angle": 40, "label": "A"}],           labeled points on the circle (degrees)
    //   "segments": [{"from": "O", "to": "A", "label": "8"}],  "O" = center; others = point labels
    //   "central_angle": {"from": 0, "to": 72, "label": "72°"}

    // rectangle:
    "width": 8, "height": 5,
    "width_label": "8", "height_label": "5"
  }
}
"""
import json
import sys
import math

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# Line colors, in the order multiple functions are drawn. Distinct in both hue and
# lightness so the figure stays readable if a student prints it in greyscale.
LINE_COLORS = ["#2563EB", "#B45309", "#047857", "#7C3AED"]
SHADE_COLOR = "#2563EB"


def eval_function(fn, x):
    """Evaluate one function spec (kind + params) over an array of x values."""
    kind = fn["kind"]
    p = fn["params"]
    if kind == "linear":
        return p["m"] * x + p["b"]
    elif kind == "quadratic":
        return p["a"] * x**2 + p["b"] * x + p["c"]
    elif kind == "absolute_value":
        return p["a"] * np.abs(x - p["h"]) + p["k"]
    elif kind == "exponential":
        return p["a"] * np.power(p["b"], x)
    elif kind == "cubic":
        return p["a"] * x**3 + p["b"] * x**2 + p["c"] * x + p["d"]
    raise ValueError(f"Unknown function kind: {kind}")


def render_graph(data, ax):
    chart_type = data["chart_type"]

    if chart_type == "function":
        if "functions" in data and "function" in data:
            raise ValueError(
                "spec supplies BOTH 'function' and 'functions' -- use one or the other, "
                "'function' for a single curve or 'functions' for two or more"
            )
        fns = data["functions"] if "functions" in data else [data["function"]]
        if not fns:
            raise ValueError("chart_type 'function' requires at least one function")
        x_min, x_max = data.get("x_range", [-10, 10])
        x = np.linspace(x_min, x_max, 400)
        for i, fn in enumerate(fns):
            ax.plot(x, eval_function(fn, x), linewidth=2,
                    color=LINE_COLORS[i % len(LINE_COLORS)],
                    label=fn.get("label"))
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        if any(fn.get("label") for fn in fns):
            ax.legend(fontsize=9, loc="best")

    elif chart_type == "inequality":
        ineqs = data.get("inequalities")
        if not ineqs:
            raise ValueError("chart_type 'inequality' requires a non-empty 'inequalities' list")
        x_min, x_max = data.get("x_range", [-10, 10])
        y_min, y_max = data.get("y_range", [-10, 10])
        x = np.linspace(x_min, x_max, 400)

        # Boundary lines: solid when the boundary itself is included (<=, >=), dashed when
        # it is excluded (<, >). This distinction is frequently the point of the question.
        for i, ineq in enumerate(ineqs):
            op = ineq.get("operator")
            if op not in ("<", "<=", ">", ">="):
                raise ValueError(
                    f"inequality {i} has operator '{op}' -- must be one of <, <=, >, >="
                )
            ax.plot(x, eval_function(ineq, x), linewidth=2,
                    color=LINE_COLORS[i % len(LINE_COLORS)],
                    linestyle="-" if op in ("<=", ">=") else "--",
                    label=ineq.get("label"))

        # Shading, computed on a grid so it works for nonlinear boundaries too.
        gx, gy = np.meshgrid(np.linspace(x_min, x_max, 400),
                             np.linspace(y_min, y_max, 400))
        masks = []
        for ineq in ineqs:
            boundary = eval_function(ineq, gx)
            op = ineq["operator"]
            if op in ("<", "<="):
                masks.append(gy <= boundary)
            else:
                masks.append(gy >= boundary)

        if data.get("shade_intersection") and len(masks) > 1:
            combined = masks[0]
            for m in masks[1:]:
                combined = combined & m
            regions = [combined]
        else:
            regions = masks

        for m in regions:
            ax.contourf(gx, gy, m.astype(float), levels=[0.5, 1.5],
                        colors=[SHADE_COLOR], alpha=0.18)

        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        if any(i.get("label") for i in ineqs):
            ax.legend(fontsize=9, loc="best")

    elif chart_type == "scatter":
        points = data["points"]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.scatter(xs, ys, color="#2563EB", zorder=3)
        if "best_fit_line" in data:
            x_min, x_max = data.get("x_range", [min(xs) - 1, max(xs) + 1])
            x = np.linspace(x_min, x_max, 100)
            bf = data["best_fit_line"]
            y = bf["m"] * x + bf["b"]
            ax.plot(x, y, linewidth=1.5, color="#0F1F3D", linestyle="--")

    elif chart_type == "bar":
        ax.bar(data["categories"], data["values"], color="#2563EB")

    else:
        raise ValueError(f"Unknown chart_type: {chart_type}")

    if "x_range" in data and chart_type != "bar":
        ax.set_xlim(data["x_range"])
    if "y_range" in data and chart_type != "bar":
        ax.set_ylim(data["y_range"])

    # Explicit tick spacing. Without this matplotlib derives spacing from the range, which
    # can put a point the student must read between labeled gridlines -- a real defect that
    # has reached critique before. See item-design-rules.md, "graph-read items".
    if chart_type != "bar":
        if data.get("x_tick_step"):
            ax.xaxis.set_major_locator(MultipleLocator(data["x_tick_step"]))
        if data.get("y_tick_step"):
            ax.yaxis.set_major_locator(MultipleLocator(data["y_tick_step"]))

    for mp in data.get("mark_points", []):
        px, py = mp["point"] if isinstance(mp, dict) else mp
        ax.scatter([px], [py], color="#0F1F3D", zorder=5, s=36)
        label = mp.get("label") if isinstance(mp, dict) else None
        if label:
            ax.annotate(label, (px, py), fontsize=11, color="#0F1F3D",
                        xytext=(6, 6), textcoords="offset points")

    ax.set_xlabel(data.get("x_label", ""))
    ax.set_ylabel(data.get("y_label", ""))
    if data.get("title"):
        ax.set_title(data["title"])
    ax.grid(True, linewidth=0.4, alpha=0.6)


def _triangle_vertices(side_lengths, right_triangle=False):
    a, b, c = side_lengths  # a, b are legs (or arbitrary sides), c is opposite the first vertex
    if right_triangle:
        # Right angle between side_a and side_b, placed at origin.
        p0 = (0, 0)
        p1 = (a, 0)
        p2 = (0, b)
        return [p0, p1, p2]
    # General triangle via law of cosines, side lengths a (P1P2), b (P0P2), c (P0P1)
    p0 = (0, 0)
    p1 = (c, 0)
    cos_angle = (b**2 + c**2 - a**2) / (2 * b * c)
    cos_angle = max(-1, min(1, cos_angle))
    angle = math.acos(cos_angle)
    p2 = (b * math.cos(angle), b * math.sin(angle))
    return [p0, p1, p2]


def render_geometry(data, ax):
    shape = data["shape"]

    if shape in ("triangle", "right_triangle"):
        side_lengths = data["side_lengths"]
        vertices = _triangle_vertices(side_lengths, right_triangle=(shape == "right_triangle"))
        vertices.append(vertices[0])
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        ax.plot(xs, ys, color="#0F1F3D", linewidth=2)

        labels = data.get("side_labels", [])
        pts = vertices[:3]
        edges = [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])]
        # Edge walk order (p0-p1, p1-p2, p2-p0) does not match side_lengths input order --
        # map explicitly so labels land on the correct edge instead of a plausible-looking wrong one.
        # right_triangle: side_lengths = [leg1 (p0-p1), leg2 (p2-p0), hypotenuse (p1-p2)]
        # triangle:       side_lengths = [a=BC opposite p0 (p1-p2), b=CA opposite p1 (p2-p0), c=AB opposite p2 (p0-p1)]
        if shape == "right_triangle":
            edge_label_index = [0, 2, 1]
        else:
            edge_label_index = [2, 0, 1]
        for i, (p_a, p_b) in enumerate(edges):
            li = edge_label_index[i]
            if li < len(labels) and labels[li]:
                mx, my = (p_a[0] + p_b[0]) / 2, (p_a[1] + p_b[1]) / 2
                ax.annotate(labels[li], (mx, my), fontsize=12, ha="center")

        angle_labels = data.get("angle_labels", [])
        for i, p in enumerate(pts):
            if i < len(angle_labels) and angle_labels[i]:
                ax.annotate(angle_labels[i], p, fontsize=11, color="#2563EB",
                            xytext=(5, 5), textcoords="offset points")
        ax.set_aspect("equal")

    elif shape == "circle":
        r = data["radius"]
        circle = plt.Circle((0, 0), r, fill=False, color="#0F1F3D", linewidth=2)
        ax.add_patch(circle)
        if data.get("radius_label"):
            ax.plot([0, r], [0, 0], color="#2563EB", linewidth=1.5)
            ax.annotate(data["radius_label"], (r / 2, 0.3), fontsize=12, color="#2563EB")
        # Optional extras (added run 79), all backward compatible:
        #   "center_label": "O"
        #   "points": [{"angle": 40, "label": "A", "distance": 1.0}, ...]  -- labeled points, angle in degrees; optional distance (run 80) = multiple of radius from center (>1 puts the point outside, e.g. tangent external point)
        #   "segments": [{"from": "O"|label, "to": "O"|label, "label": "8"}, ...] -- chords/radii/diameters
        #   "central_angle": {"from": 0, "to": 72, "label": "72°"} -- wedge from the center, degrees
        if data.get("center_label"):
            ax.plot([0], [0], "o", color="#0F1F3D", markersize=4)
            ax.annotate(data["center_label"], (0, 0), fontsize=12, xytext=(-12, -14),
                        textcoords="offset points")
        coords = {"O": (0.0, 0.0)}
        for pt in data.get("points", []):
            a = math.radians(pt["angle"])
            d = r * pt.get("distance", 1.0)  # optional (run 80): distance from center in units of r, >1 = outside circle
            coords[pt["label"]] = (d * math.cos(a), d * math.sin(a))
            ax.plot([coords[pt["label"]][0]], [coords[pt["label"]][1]], "o",
                    color="#0F1F3D", markersize=4)
            ax.annotate(pt["label"], coords[pt["label"]], fontsize=12,
                        xytext=(8 * math.cos(a) - 4, 8 * math.sin(a) - 4),
                        textcoords="offset points")
        for seg in data.get("segments", []):
            p, q = coords[seg["from"]], coords[seg["to"]]
            ax.plot([p[0], q[0]], [p[1], q[1]], color="#2563EB", linewidth=1.5)
            if seg.get("label"):
                ax.annotate(seg["label"], ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), fontsize=12,
                            color="#2563EB", xytext=(4, 5), textcoords="offset points")
        ca = data.get("central_angle")
        if ca:
            a0, a1 = ca["from"], ca["to"]
            ts = np.radians(np.linspace(a0, a1, 60))
            ax.fill(np.concatenate([[0], r * np.cos(ts)]), np.concatenate([[0], r * np.sin(ts)]),
                    color="#2563EB", alpha=0.12)
            for a in (a0, a1):
                ax.plot([0, r * math.cos(math.radians(a))], [0, r * math.sin(math.radians(a))],
                        color="#2563EB", linewidth=1.5)
            if ca.get("label"):
                mid = math.radians((a0 + a1) / 2)
                ax.annotate(ca["label"], (0.45 * r * math.cos(mid), 0.45 * r * math.sin(mid)),
                            fontsize=11, color="#2563EB", ha="center", va="center")
        ext = max([r] + [max(abs(c[0]), abs(c[1])) for c in coords.values()])
        ax.set_xlim(-ext * 1.3 if ext > r else -r * 1.3, ext * 1.3)
        ax.set_ylim(-ext * 1.3 if ext > r else -r * 1.3, ext * 1.3)
        ax.set_aspect("equal")

    elif shape == "rectangle":
        w, h = data["width"], data["height"]
        rect = plt.Rectangle((0, 0), w, h, fill=False, color="#0F1F3D", linewidth=2)
        ax.add_patch(rect)
        if data.get("width_label"):
            ax.annotate(data["width_label"], (w / 2, -h * 0.1), fontsize=12, ha="center")
        if data.get("height_label"):
            ax.annotate(data["height_label"], (-w * 0.1, h / 2), fontsize=12, va="center", ha="right")
        ax.set_xlim(-w * 0.3, w * 1.3)
        ax.set_ylim(-h * 0.3, h * 1.3)
        ax.set_aspect("equal")

    else:
        raise ValueError(f"Unknown shape: {shape}")

    ax.axis("off")


def main():
    if len(sys.argv) != 3:
        print("Usage: python render_visual.py <spec.json> <output.svg>")
        sys.exit(2)

    spec_path, out_path = sys.argv[1], sys.argv[2]
    with open(spec_path) as f:
        spec = json.load(f)

    visual_type = spec["visual_type"]
    data = spec["visual_data"]

    fig, ax = plt.subplots(figsize=(5, 4))

    if visual_type == "graph":
        render_graph(data, ax)
    elif visual_type == "geometry":
        render_geometry(data, ax)
    else:
        print(f"ERROR: render_visual.py doesn't handle visual_type '{visual_type}' -- "
              f"'table' needs no rendering, it's plain structured data.")
        sys.exit(2)

    fig.tight_layout()
    fig.savefig(out_path, format="svg")
    plt.close(fig)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
