import copy
import uuid

class TrackChange:
    def __init__(self):
        self.did_change = False

    def track_change(self, did_change: bool):
        if did_change:
            self.did_change = True

    @property
    def changed(self):
        return self.did_change

    def __str__(self):
        return 'Changed!' if self.changed else 'Not Changed'

class Node:
    _debug = False

    def __init__(self, identifier, permanent_node: bool=False):
        self.identifier = identifier
        self._in_paths: ["Path"] = []
        self._out_paths: ["Path"] = []
        self.permanent_node = permanent_node  # e.g. first node or last node.

    def add_path_in(self, path: "Path") -> bool:
        for p in self._in_paths:
            if p.uuid == path.uuid:
                return False

        self._in_paths.append(path)
        path.update_to_node(self)

    def add_path_out(self, path: "Path") -> bool:
        for p in self._out_paths:
            if p.uuid == path.uuid:
                return False

        self._out_paths.append(path)
        path.update_from_node(self)

    @property
    def len_in_paths(self):
        return len(self._in_paths)

    @property
    def len_out_paths(self):
        return len(self._out_paths)

    @property
    def in_paths(self):
        return self._in_paths

    @property
    def out_paths(self):
        return self._out_paths

    def remove_in_path(self, path: "Path") -> bool:
        found_path = False
        for i in range(len(self._in_paths), -1, -1):
            if i >= len(self._in_paths):
                continue

            if self._in_paths[i] == path:
                if Node._debug: print(f'Remove in-path from {str(path)}')
                self._in_paths.pop(i)
                path.update_to_node(None)
                found_path = True
        return found_path

    def remove_out_path(self, path: "Path") -> bool:
        found_path = False
        for i in range(len(self._out_paths), -1, -1):
            if i >= len(self._out_paths):
                continue

            if self._out_paths[i] == path:
                if Node._debug: print(f'Remove out-path from {str(path)}')
                self._out_paths.pop(i)
                path.update_from_node(None)
                found_path = True
        return found_path

    def remove_in_paths(self) -> bool:
        track_change = TrackChange()

        p: Path
        for p in self._in_paths:
            from_node = p._from_node
            if from_node:
                track_change.track_change(from_node.remove_out_path(p))
                p.update_to_node(None)

            track_change.track_change(p.update_to_node(None))

        self._in_paths = []

        return track_change.changed

    def remove_out_paths(self) -> bool:
        track_change = TrackChange()

        p: Path
        for p in self._out_paths:
            to_node = p.to_node
            if to_node:
                track_change.track_change(to_node.remove_in_path(p))
                p.update_to_node(None)

            track_change.track_change(p.update_from_node(None))

        self._out_paths = []
        return track_change.changed

    def _consolidate_in_paths(self) -> bool:
        """
        When the number of out paths is one, we can point all in paths to the target of the single out path, thus
        removing this node from the path.
        :return:
        """
        assert len(self._out_paths) == 1
        old_out: Path = self._out_paths[0]
        new_to_node: Node = old_out.to_node

        track_change = TrackChange()
        p: Path
        while self._in_paths:
            p = self._in_paths[0]
            if Node._debug: print(f'  - Update path from {p.from_node.identifier} to {p.to_node.identifier} to point to {new_to_node.identifier}')
            track_change.track_change(p.update_to_node(new_to_node))

        old_out.update_from_node(None)
        old_out.update_to_node(None)
        return track_change.changed

    def _remove_duplicates(self, paths: ["Path"]) -> bool:
        track_change = TrackChange()

        duplicates = []
        p1: Path
        for p1 in paths:
            p2: Path
            for p2 in paths:
                if p1 != p2 and p1.from_node == p2.from_node and p1.to_node == p2.to_node:
                    duplicates.append(p2)

        if duplicates:
            track_change.track_change(True)
            duplicates = duplicates[1:]
            while duplicates:
                duplicate: Path = duplicates.pop()
                duplicate.update_to_node(None)
                duplicate.update_from_node(None)

        return track_change.changed

    def remove_duplicates(self) -> bool:
        track_change = TrackChange()
        track_change.track_change(self._remove_duplicates(self._in_paths))
        track_change.track_change(self._remove_duplicates(self._out_paths))

        return track_change.changed

    # ToDo: Create prune(), prune_backward() and prune_forward() functions:
    # prune_backward()
    # If the number of out paths is zero, for each incoming path:
    #   - save the 'from' node
    #   - disconnect the path (set from and to to None)
    #   - call prune_backward() on the 'from' node.
    #
    # prune_forward()
    # Same approach, but look at the to node and call prune_forward()

    def prune_backward(self) -> bool:
        if self.permanent_node or len(self.out_paths) != 0 or len(self.in_paths) == 0:
            return False

        for path in self.in_paths:
            from_node = path.from_node
            path.disconnect()
            from_node.prune_backward()

        return True

    def prune_forward(self) -> bool:
        if self.permanent_node or len(self.in_paths) != 0 or len(self.out_paths) == 0:
            return False

        for path in self.out_paths:
            to_node = path.to_node
            path.disconnect()
            to_node.prune_forward()

        return True

    def simplify(self) -> bool:
        track_change = TrackChange()

        if self.permanent_node:
            return False

        if len(self._out_paths) == 0:
            if Node._debug: print(f'Remove in-paths from node {str(self)} with no out paths')
            track_change.track_change(self.remove_in_paths())
        elif len(self._out_paths) == 1:
            if Node._debug: print(f'Consolidate in paths from node {str(self)} with one out paths')
            track_change.track_change(self._consolidate_in_paths())

        return track_change.changed

    def __str__(self):
        return f'[{len(self._in_paths)}] {str(self.identifier)} [{len(self._out_paths)}]'


class Path:
    _debug = False
    def __init__(self,
                 from_node: Node,
                 to_node: Node,
                 description='-'):
        self.uuid = uuid.uuid4()
        self._from_node: Node = from_node
        self._to_node: Node = to_node
        self._from_node.add_path_out(self)
        self._to_node.add_path_in(self)
        self._description = description

    def __eq__(self, other: "Path"):
        return self.uuid == other.uuid

    def __str__(self):
        from_node = self._from_node.identifier if self._from_node else "-"
        to_node = self._to_node.identifier if self._to_node else "-"
        return f'{from_node} [{str(self.uuid)[-5:]} / {self._description}] {to_node}'

    @property
    def description(self):
        return self._description

    @property
    def from_node(self):
        return self._from_node

    @property
    def to_node(self):
        return self._to_node

    def update_to_node(self, to_node: Node|None) -> bool:
        if to_node == self._to_node:
            return False

        if Path._debug: print(f'Update to-node for {str(self)} from {str(self._to_node or "None")} to {str(to_node) or "None"}')

        if self.to_node:
            self._to_node.remove_in_path(self)
            self._to_node = None

        self._to_node = to_node
        if to_node:
            to_node.add_path_in(self)

        return True

    def update_from_node(self, from_node: Node|None):
        if from_node == self._from_node:
            return False

        if Path._debug: print(f'Update to-node from for {str(self)} {str(self.to_node or "None")} to {str(from_node) or "None"}')

        if self._from_node:
            self._from_node.remove_out_path(self)
            self._from_node = None

        self._from_node = from_node
        if from_node:
            from_node.add_path_in(self)

        return True

    def disconnect(self):
        self.update_from_node(None)
        self.update_to_node(None)

    def join(self, from_node: Node, to_node: Node):
        self.update_from_node(from_node)
        self.update_to_node(to_node)


class Graph:
    _debug = False

    def __init__(self):
        self.paths: [Path] = []
        self.nodes: [Node] = []

    def __str__(self):
        return f'{len(self.paths)} paths and {len(self.nodes)} nodes'

    def groom_paths(self) -> int:
        """
        Identify any paths that are orphaned and delete them.

        :return: number of changes made
        """
        num_changes = 0
        made_change = True
        while made_change:
            made_change = False
            for i in range(len(self.paths), -1, -1):
                if i >= len(self.paths):
                    continue

                path: Path = self.paths[i]
                if path.to_node is None and path.from_node is None:
                    if Graph._debug: print(f"Delete orphaned path {str(path)}")
                    self.paths.pop(i)
                    del path
                    made_change = True
                    num_changes += 1

        return num_changes

    def prune_nodes(self) -> bool:
        track_change = TrackChange()

        for node in self.nodes:
            track_change.track_change(node.prune_backward())
            track_change.track_change(node.prune_forward())

        return track_change.changed

    def groom_nodes(self) -> int:
        num_changes = 0
        made_change = True
        while made_change:
            made_change = False
            for i in range(len(self.nodes), -1, -1):
                if i >= len(self.nodes):
                    continue

                node: Node = self.nodes[i]
                if not node.permanent_node and node.len_in_paths == node.len_out_paths == 0:
                    if Graph._debug: print(f"Delete orphaned node {str(node)}")
                    self.nodes.pop(i)
                    del node
                    made_change = True
                    num_changes += 1
        return num_changes


    def simplify_nodes(self) -> int:
        num_changes = 0
        made_change = True
        while made_change:
            made_change = False
            node: Node
            for node in self.nodes:
                if node.simplify():
                    made_change = True
                    num_changes += 1

        return num_changes


    def remove_duplicates(self) -> bool:
        track_change = TrackChange()

        for node in self.nodes:
            track_change.track_change(node.remove_duplicates())

        return track_change.changed

    def groom(self):
        # Important! We must remove duplicates before we simplify to avoid over-collapsing
        while self.remove_duplicates():
            pass

        self.simplify_nodes()
        while self.groom_paths():
            pass

        while self.groom_nodes():
            pass


    def walk(self, node: Node|None=None):
        if node is None:
            if len(self.nodes) == 0:
                print('No nodes to walk!')
                return

            node = self.nodes[0]

        for path in node._out_paths:
            to_node = path._to_node
            if path.description:
                print(f'{node.identifier} -> {path.description} -> {to_node.identifier if to_node else "-"}')
            else:
                print(f'{node.identifier} -> {to_node.identifier if to_node else "-"}')
            if to_node:
                self.walk(to_node)

    def count_paths(self, exclude_nodes: [Node]) -> int:
        total_paths = 1
        for node in self.nodes:
            if [n for n in exclude_nodes if n.identifier == node.identifier]:
                continue

            total_paths *= node.len_out_paths

        return total_paths

    def find_node(self, node_id) -> Node:
        nodes = [n for n in self.nodes if n.identifier == node_id]
        if nodes:
            return nodes[0]
        else:
            return None

    def set_node_permantent(self, node_id: str):
        node = self.find_node(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found")

    def initialize(self, node_ids: [str]):
        prior_node = None
        for node_id in node_ids:
            node = self.find_node(node_id)
            if node is None:
                node = Node(node_id)
                self.nodes.append(node)

            if prior_node:
                path = Path(prior_node, node)
                self.paths.append(path)

            prior_node = node