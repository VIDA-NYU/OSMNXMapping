import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from beartype import beartype
from typing import Any, Optional, Union, List

from osmnx_mapping.modules.visualiser.abc_visualiser import VisualiserBase


class StaticVisualiser(VisualiserBase):
    @beartype
    def _render(
        self,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        target: str = "edges",
        colormap: str = "Greens",
        edge_line_width: float = 0.5,
        node_size: int = 50,
        missing_value_color: Optional[str] = None,
        colorbar_label: str = "Aggregated Value",
        **kwargs,
    ) -> Any:
        if isinstance(result_columns, list):
            if len(result_columns) > 1:
                raise ValueError(
                    "StaticVisualiser only supports a single result_column."
                )
            result_column = result_columns[0]
        else:
            result_column = result_columns

        missing_value_color = missing_value_color or "#cccccc"

        if target == "edges":
            edge_colors = ox.plot.get_edge_colors_by_attr(
                graph,
                attr=result_column,
                cmap=colormap,
                na_color=missing_value_color,
            )
            fig, ax = ox.plot.plot_graph(
                graph,
                edge_color=edge_colors,
                node_size=0,
                edge_linewidth=edge_line_width,
                show=False,
                close=True,
            )
            min_val = edges[result_column].min()
            max_val = edges[result_column].max()
        elif target == "nodes":
            node_colors = ox.plot.get_node_colors_by_attr(
                graph,
                attr=result_column,
                cmap=colormap,
                na_color=missing_value_color,
            )
            fig, ax = ox.plot.plot_graph(
                graph,
                node_color=node_colors,
                node_size=node_size,
                edge_color="gray",
                edge_linewidth=edge_line_width,
                show=False,
                close=True,
            )
            min_val = nodes[result_column].min()
            max_val = nodes[result_column].max()
        elif target == "both":
            edge_colors = ox.plot.get_edge_colors_by_attr(
                graph,
                attr=result_column,
                cmap=colormap,
                na_color=missing_value_color,
            )
            node_colors = ox.plot.get_node_colors_by_attr(
                graph,
                attr=result_column,
                cmap=colormap,
                na_color=missing_value_color,
            )
            fig, ax = ox.plot.plot_graph(
                graph,
                edge_color=edge_colors,
                node_color=node_colors,
                node_size=node_size,
                edge_linewidth=edge_line_width,
                show=False,
                close=True,
            )
            min_val = min(edges[result_column].min(), nodes[result_column].min())
            max_val = max(edges[result_column].max(), nodes[result_column].max())
        else:
            raise ValueError("target must be 'nodes', 'edges', or 'both'")

        if min_val == max_val:
            min_val, max_val = 0, 1

        norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
        scalar_mappable = cm.ScalarMappable(norm=norm, cmap=colormap)
        scalar_mappable._A = []
        fig.colorbar(scalar_mappable, ax=ax, label=colorbar_label)

        return fig
