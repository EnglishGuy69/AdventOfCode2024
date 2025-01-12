
import pytest

from graph import Node, Path, Graph, TrackChange

Node._debug = True
Path._debug = True
Graph._debug = True

def test_track_change():
    track_change = TrackChange()

    track_change.track_change(False)
    assert track_change.changed == False

    track_change.track_change(True)
    assert track_change.changed

    track_change.track_change(False)
    assert track_change.changed

    pass

def test_remove_duplicates():

    a = Node('a')
    b = Node('b')
    c = Node('c')

    ab1 = Path(a,b)
    ab2 = Path(a,b)
    ac1 = Path(a,c)
    bc1 = Path(b,c)

    for node in [a,b,c]:
        node.remove_duplicates()

    pass

def test_consolidate():
    """
       *           *
       A---B---C---D

       A---D

       * = permanent node
    :return:
    """
    graph = Graph()
    a = Node('A', permanent_node=True)
    b = Node('C')
    c = Node('D')
    d = Node('D', permanent_node=True)

    ab = Path(a,b)
    bc = Path(b,c)
    cd = Path(c,d)

    graph.nodes.extend([a,b,c,d])
    graph.paths.extend([ab, bc, cd])

    graph.groom()
    assert a.len_out_paths == 1
    assert b.len_in_paths == b.len_out_paths == 0
    assert c.len_in_paths == c.len_out_paths == 0
    assert d.len_in_paths == 1
    assert a.out_paths[0].to_node.identifier == 'D'
    assert d.in_paths[0].from_node.identifier == 'A'


def test_truncate():
    """
       *
       A---B---C---D

       A

       * = permanent node
    :return:
    """
    graph = Graph()
    a = Node('A', permanent_node=True)
    b = Node('C')
    c = Node('D')
    d = Node('D')

    ab = Path(a, b)
    bc = Path(b, c)
    cd = Path(c, d)

    graph.nodes.extend([a, b, c, d])
    graph.paths.extend([ab, bc, cd])

    graph.groom()
    assert a.len_out_paths == 0
    assert b.len_in_paths == b.len_out_paths == 0
    assert c.len_in_paths == c.len_out_paths == 0
    assert d.len_in_paths == 0

    pass

def test_dual():
    """
       *                   *
       A---B---C------E----F
        \     / \    / \  /
         \---/   \--/   \/

       A---F
        \_/

       * = permanent node
    :return:
    """
    graph = Graph()
    a = Node('0', permanent_node=True)
    b = Node('1')
    c = Node('2')
    d = Node('3')
    e = Node('4')
    f = Node('5', permanent_node=True)

    ab = Path(a, b,'b')
    bc = Path(b, c, description='r')
    ce = Path(c, e, description='wr')
    ef = Path(e, f, description='r')

    ac2 = Path(a, c,'br')
    ce2 = Path(c, e, description='wr')
    ef2 = Path(e, f, description='r')

    graph.nodes.extend([a, b, c, d, e, f])
    graph.paths.extend([ab, bc, ce, ef, ac2, ce2, ef2])

    graph.groom()
    graph.walk()


    pass

def test_prune_backward():
    """
        *
        A--B--C   *
         \--D--E--F

    to

        *        *
        A--D--E--F

    :return:
    """
    graph = Graph()

    graph.initialize(['A','B','C'])
    graph.initialize(['A','D','E','F'])
    graph.set_node_permantent('A')
    graph.set_node_permantent('F')

    c = graph.find_node('C')
    c.prune_backward()
    graph.groom_nodes()

    assert graph.find_node('A').len_out_paths == 1 and graph.find_node('A').out_paths[0].to_node.identifier == 'D'
    assert graph.find_node('D').len_out_paths == 1 and graph.find_node('D').out_paths[0].to_node.identifier == 'E'
    assert graph.find_node('E').len_out_paths == 1 and graph.find_node('E').out_paths[0].to_node.identifier == 'F'
    assert graph.find_node('F').len_out_paths == 0

    assert graph.find_node('B') is None
    assert graph.find_node('C') is None
    pass

def test_prune_backward():
    """
        *        *
        A--B----C
               /
        D--E--F

    to

        *       *
        A--B----C

    :return:
    """
    graph = Graph()

    graph.initialize(['A','B','C'])
    graph.initialize(['D','E','F','C'])
    graph.set_node_permantent('A')
    graph.set_node_permantent('C')

    c = graph.find_node('D')
    c.prune_forward()
    graph.groom_nodes()

    assert graph.find_node('A').len_out_paths == 1 and graph.find_node('A').out_paths[0].to_node.identifier == 'B'
    assert graph.find_node('B').len_out_paths == 1 and graph.find_node('B').out_paths[0].to_node.identifier == 'C'
    assert graph.find_node('C').len_in_paths == 1

    assert graph.find_node('D') is None
    assert graph.find_node('E') is None
    assert graph.find_node('F') is None
    pass



def test_complex():
    """
    A---B---D
    |
    C---E---G---H----J
    |       |        |
    F       I--------|
    |                |
    |----------------|

    A
    |
    C-------G--------J
    |       |        |
    |       |--------|
    |                |
    |----------------|

    """
    graph = Graph()

    a = Node('A', permanent_node=True)
    b = Node('B')
    c = Node('C')
    d = Node('D')
    e = Node('E')
    f = Node('F')
    g = Node('G')
    h = Node('H')
    i = Node('I')
    j = Node('J', permanent_node=True)
    graph.nodes.append(a)
    graph.nodes.append(b)
    graph.nodes.append(c)
    graph.nodes.append(d)
    graph.nodes.append(e)
    graph.nodes.append(f)
    graph.nodes.append(g)
    graph.nodes.append(h)
    graph.nodes.append(i)
    graph.nodes.append(j)

    ab = Path(a, b)
    bd = Path(b, d)
    ac = Path(a, c)
    ce = Path(c, e)
    cf = Path(c, f)
    eg = Path(e, g)
    gh = Path(g, h)
    hj = Path(h, j)
    gi = Path(g, i)
    ij = Path(i, j)
    fj = Path(f, j)
    graph.paths.append(ab)
    graph.paths.append(bd)
    graph.paths.append(ac)
    graph.paths.append(ce)
    graph.paths.append(cf)
    graph.paths.append(eg)
    graph.paths.append(gh)
    graph.paths.append(hj)
    graph.paths.append(gi)
    graph.paths.append(ij)
    graph.paths.append(fj)

    graph.groom()

    """
        A
        |
        C-------G--------J
        |       |        |
        |       |--------|
        |                |        
        |----------------|
    """

    assert a.len_out_paths == 1 and a.out_paths[0].to_node.identifier == 'C'
    assert b.len_in_paths == b.len_out_paths == 0
    assert c.len_out_paths == 2 and a.out_paths[0].to_node.identifier == 'C'
    assert d.len_in_paths == d.len_out_paths == 0
    assert e.len_in_paths == e.len_out_paths == 0
    assert f.len_in_paths == f.len_out_paths == 0
    assert h.len_in_paths == h.len_out_paths == 0
    assert i.len_in_paths == i.len_out_paths == 0

    graph.walk(a)
    pass


