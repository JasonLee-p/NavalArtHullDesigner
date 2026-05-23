# -*- coding: utf-8 -*-
import numpy as np

from pyqtOpenGL.items.MeshData import SymetryCylinderMesh, vertex_normal_smooth, vertex_normal_smooth_by_position


def test_vertex_normal_smooth_handles_face_index_arrays():
    verts = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0],
        [0, 0, 0], [0, 1, 0], [0, 0, 1],
    ], dtype=np.float32)
    faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)

    normals = vertex_normal_smooth(verts, faces)

    assert normals.shape == verts.shape
    assert np.all(np.linalg.norm(normals, axis=1) > 0.99)


def test_vertex_normal_smooth_by_position_welds_duplicate_vertices():
    verts = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0],
        [0, 0, 0], [0, 1, 0], [0, 0, 1],
    ], dtype=np.float32)

    normals = vertex_normal_smooth_by_position(verts)

    np.testing.assert_allclose(normals[0], normals[3], atol=1e-6)


def test_vertex_normal_smooth_by_position_preserves_sharp_edges():
    verts = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0],
        [0, 0, 0], [0, 1, 0], [0, 0, 1],
    ], dtype=np.float32)

    normals = vertex_normal_smooth_by_position(verts, smooth_angle_degrees=45)

    assert np.dot(normals[0], normals[3]) < 0.1


def test_symetry_cylinder_mesh_keeps_valid_smoothed_normals():
    points = np.array([[0, -1], [1, -1], [1, 1], [0, 1]], dtype=np.float32)
    mesh = SymetryCylinderMesh("z")
    mesh.initPoints(points, points.copy(), 1, 0)
    mesh.initVertexes()
    side_start = mesh.top_vert.shape[0] + mesh.bottom_vert.shape[0]

    assert mesh.vertexes.shape == mesh.normals.shape
    assert np.isfinite(mesh.normals).all()
    non_zero_side_normals = np.linalg.norm(mesh.normals[side_start:], axis=1) > 0.99
    assert np.count_nonzero(non_zero_side_normals) >= len(non_zero_side_normals) // 2
