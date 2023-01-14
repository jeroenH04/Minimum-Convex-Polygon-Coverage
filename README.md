
# CG:SHOP 2023

Implementation for the CG:SHOP 2023 challenge: Minimum Coverage by Convex Polygons.
https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2023

The implementation creates a triangulation using ear-clipping after which the Hertel Mehlhorn algorithm is used to combine these triangles into convex polygons.


## Installation

To run the code, run the ```main.py``` file after changing the ```instance_name``` that is passed to the ```main``` function. 
The instance ```instance_name``` should be saved in ```instances```, adhering the following format:


```bash
{
    "type": "CGSHOP2023_Instance",
    "name": "example_instance1",
    "n": 9,
    "outer_boundary": [
        {"x": 128, "y": 128},
        {"x": 192, "y": 64},
        {"x": 192, "y": 144},
        {"x": 272, "y": 160},
        {"x": 192, "y": 192}
    ],
    "holes": [
        [
            {"x": 176, "y": 144},
            {"x": 160, "y": 144},
            {"x": 160, "y": 128},
            {"x": 176, "y": 112}
        ],
        [
            ... other hole ...
        ]
    ]
}
```
By default, the function will plot both the triangulation and the polygons after applying the Hertel Mehlhorn. Furthermore, it will export the convex polygons in the following format:
```bash
{
	"type": "CGSHOP2023_Solution",
	"instance": "example_instance1",
	"polygons": [
		[
			{"x": {"num": 192, "den": 1}, "y": {"num": 288, "den": 2}},
			{"x": 272, "y": 160},
			{"x": 192, "y": 192},
			{"x": 144, "y": 144}
		],
		[
			{"x": 192, "y": 144},
			{"x": 176, "y": 144},
			{"x": 176, "y": 80},
			{"x": 192, "y": 64}
		],
		[
			{"x": 144, "y": 144},
			{"x": 160, "y": 128},
			{"x": 160, "y": 144}
		],
		[
			{"x": 192, "y": 64},
			{"x": 192, "y": 96},
			{"x": 144, "y": 144},
			{"x": 128, "y": 128}
		]
	]
}
```
## Authors

- [Jeroen Hellenbrand](https://www.github.com/jeroenH04)
- [Thomas Heij](https://www.github.com/tjheij)
- [Sam Nijsten](https://www.github.com/sammo11r)

## Acknowledgements

 - [Ear-clipping Based Algorithms of Generating High-quality Polygon Triangulation](https://arxiv.org/abs/1212.6038)
 - [Fast triangulation of the plane with respect to simple polygons](https://www.sciencedirect.com/science/article/pii/S0019995885800449)
 - [Computational Geometry in C](https://doi.org/10.1017/CBO9780511804120)

