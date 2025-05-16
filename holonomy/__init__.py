import trimesh

from holonomy.examples.square_antiprism import square_antiprism
from holonomy.generate import generate_pegs
from holonomy.generate.model3d import (
    PegsConfig,
    SectionConfig,
    add_pegs,
    construct_grooves,
    create_groove_section,
    cylinder_intersections,
)


def main():
    network = generate_pegs(square_antiprism)
    assert network is not None

    sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.98)
    config = SectionConfig(
        height=0.2,
        width=0.35,
        rail_height=0.1,
        rail_width=0.06,
        bottleneck_height=0.08,
        bottleneck_width=0.16,
    )

    pegs_config = PegsConfig(height=0.1, radius=0.05)
    peg_meshes = add_pegs(network, pegs_config, config)
    sphere = trimesh.boolean.union([sphere, *peg_meshes])
    section = create_groove_section(config)
    grooves = construct_grooves(network, section)

    cylinders = cylinder_intersections(config, network)

    sphere = trimesh.boolean.difference([sphere, *grooves, *cylinders])
    sphere.show()


if __name__ == "__main__":
    main()
