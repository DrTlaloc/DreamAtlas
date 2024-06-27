# Imports all the DreamAtlas functionality and dependencies
from . import *


def plot_map_class(map_class):

    surface_pixel_map = map_class.surface_pixel_map
    ug_pixel_map = map_class.ug_pixel_map
    layout = map_class.layout
    x_size, y_size = map_class.map_size

    # Making the figures (general map, regions, terrain, population)
    fig1, (surface1, cave1) = plt.subplots(2, 1)
    fig2, (surface2, cave2) = plt.subplots(2, 1)
    fig3, (surface3, cave3) = plt.subplots(2, 1)
    fig4, (surface4, cave4) = plt.subplots(2, 1)

    surface_axs = [surface1, surface2, surface3, surface4]
    cave_axs = [cave1, cave2, cave3, cave4]

    for ax in surface_axs:
        ax.set(xlim=[0, x_size], ylim=[0, y_size])
    for ax in cave_axs:
        ax.set(xlim=[0, x_size], ylim=[0, y_size])

    # Make the surface objects to be plotted
    surface_general = np.zeros([y_size, x_size])
    surface_regions = np.zeros([y_size, x_size])
    surface_terrain = np.zeros([y_size, x_size])
    surface_population = np.zeros([y_size, x_size])

    province_dict = {}
    for province in map_class.province_list:
        province_dict[province.index] = province

    for x in range(x_size):
        for y in range(y_size):
            this_index = surface_pixel_map[x, y]
            if this_index == 0:
                this_index = 1
            province = province_dict[this_index]
            surface_general[y, x] = this_index
            surface_regions[y, x] = province.parent_region
            terrain_list = terrain_int2list(province.terrain_int)
            for terrain in terrain_list:
                surface_terrain[y, x] += TERRAIN_2_HEIGHTS_DICT[terrain]
            surface_population[y, x] = province.population

    # Make the underground objects to be plotted
    cave_general = np.zeros([y_size, x_size])
    cave_regions = np.zeros([y_size, x_size])
    cave_terrain = np.zeros([y_size, x_size])
    cave_population = np.zeros([y_size, x_size])

    for x in range(x_size):
        for y in range(y_size):
            this_index = ug_pixel_map[x, y]
            if this_index == 0:
                this_index = 1
            province = province_dict[this_index]
            cave_general[y, x] = this_index
            cave_regions[y, x] = province.parent_region
            terrain_list = terrain_int2list(province.terrain_int)
            for terrain in terrain_list:
                cave_terrain[y, x] += TERRAIN_2_HEIGHTS_DICT[terrain]
            cave_population[y, x] = province.population

    # Plotting the contourf and the province border contour map
    surface1.imshow(surface_general, cmap=cm.Pastel1)
    surface2.imshow(surface_regions, vmin=1, vmax=len(layout.region_graph), cmap=cm.tab20)
    surface3.imshow(surface_terrain,  vmin=-200, vmax=600, cmap=cm.terrain)
    surface4.imshow(surface_population, cmap=cm.YlGn)
    for ax in surface_axs:
        ax.contour(surface_general, levels=max(layout.surface_graph), colors=['white', ])

    # Plotting the contourf and the province border contour map
    cave1.imshow(cave_general, cmap=cm.Pastel1)
    cave2.imshow(cave_regions, vmin=1, vmax=len(layout.region_graph), cmap=cm.tab20)
    cave3.imshow(cave_terrain,  vmin=-200, vmax=600, cmap=cm.terrain)
    cave4.imshow(cave_population, cmap=cm.YlGn)
    for ax in cave_axs:
        ax.contour(cave_general, levels=max(layout.ug_graph), colors=['white', ])

    virtual_graph, virtual_coordinates = make_virtual_graph(layout.surface_graph, layout.surface_coordinates, layout.surface_darts, map_class.map_size)
    for i in virtual_graph:
        x0, y0 = virtual_coordinates[i]
        for j in virtual_graph[i]:
            x1, y1 = virtual_coordinates[j]
            for ax in surface_axs:
                ax.plot([x0, x1], [y0, y1], 'k-')

    for i in virtual_graph:
        if i <= max(layout.surface_graph):
            x0, y0 = virtual_coordinates[i]
            for ax in surface_axs:
                ax.plot(x0, y0, 'ro')
                ax.text(x0, y0, str(i))

    # Making the underground connection/node overlay
    virtual_graph, virtual_coordinates = make_virtual_graph(layout.ug_graph, layout.ug_coordinates, layout.ug_darts, map_class.map_size)
    for i in virtual_graph:
        x0, y0 = virtual_coordinates[i]
        for j in virtual_graph[i]:
            x1, y1 = virtual_coordinates[j]
            for ax in cave_axs:
                ax.plot([x0, x1], [y0, y1], 'k-')

    for i in virtual_graph:
        if i <= max(layout.ug_graph):
            x0, y0 = virtual_coordinates[i]
            for ax in cave_axs:
                ax.plot(x0, y0, 'ro')
                ax.text(x0, y0, str(i))


def plot_region(region, terrain=True, population=True):

    # Making the figures (graph, terrain, population)
    fig, axs = plt.subplots(1, 1 + terrain + population)
    ax_graph = axs[0]
    plot_size = [500, 500]
    z_graph = np.zeros(plot_size)
    if terrain:
        ax_terrain = axs[1]
        z_terrain = np.zeros(plot_size)
    if population:
        ax_population = axs[2]
        z_population = np.zeros(plot_size)

    # Make the contourf z objects to be plotted
    points = []
    for province in region.provinces:
        index = province.index
        x, y = province.coordinates
        points.append([index, x, y])

    pixel_map = find_pixel_ownership(points, plot_size, hwrap=False, vwrap=False, scale_down=8, minkowski_dist=3)
    for x in range(plot_size[0]):
        for y in range(plot_size[1]):
            this_index = pixel_map[x][y]
            z_graph[y][x] = this_index
            if terrain:
                terrain_list = terrain_int2list(region.provinces[this_index-1].terrain_int)
                for terrain in terrain_list:
                    z_terrain[y][x] += TERRAIN_2_HEIGHTS_DICT[terrain]
            if population:
                z_population[y][x] = region.provinces[this_index-1].population

    # Plotting the contourf and the province border contour map
    levels = len(region.graph)
    ax_graph.imshow(z_graph, cmap=cm.Set1)
    ax_graph.contour(z_graph, levels=levels, colors=['white',])
    ax_graph.set_title('Provinces')
    if terrain:
        ax_terrain.imshow(z_terrain,  vmin=-200, vmax=600, cmap=cm.terrain)
        ax_terrain.contour(z_graph, levels=levels, colors=['white',])
        ax_terrain.set_title('Terrain')
    if population:
        ax_population.imshow(z_population,  vmin=0, vmax=45000, cmap=cm.YlGn)
        ax_population.contour(z_graph, levels=levels, colors=['white',])
        ax_population.set_title('Population')

    name = ''
    for nation in region.nations:
        name = name + ' +' + nation.name
    fig.suptitle('%s Region' % name)


def plot_torus_graph(graph, coordinates, ax=None, real_size=None):

    if ax is None:
        _ = plt.figure()
        ax = plt.axes()

    if real_size is None:
        real_size = np.Inf

    for vertex in range(len(graph)):
        x0, y0 = coordinates[vertex + 1]
        for edge in graph[vertex + 1]:
            x1, y1 = coordinates[edge]
            ax.plot([x0, x1], [y0, y1], 'k-')

    for vertex in range(len(graph)):
        x0, y0 = coordinates[vertex + 1]
        if vertex > real_size-1:
            ax.plot(x0, y0, 'go')
            ax.text(x0, y0, str(vertex + 1))
        else:
            ax.plot(x0, y0, 'ro')
            ax.text(x0, y0, str(vertex + 1))

    ax.set(xlim=(0, 2000), ylim=(0, 1000))