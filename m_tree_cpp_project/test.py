import m_tree
import pickle



a = m_tree.test_mesher()

vertices = a.get_vertices()
polygons = a.get_polygons()


save_path = r"D:\Blender\m_tree\save.pkl"
with open(save_path, 'wb') as f:
    pickle.dump([vertices,polygons], f)


