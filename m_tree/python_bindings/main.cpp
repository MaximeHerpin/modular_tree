#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
// #include <mtree-lib/BaseTypes/Node.hpp>
//#include "./BaseTypes/Mesh.hpp"
#include "../source/BaseTypes/Node.hpp"
// #include "../source/BaseTypes/Mesh.hpp"
// #include "../source/BaseTypes/Tree.hpp"
// #include "../source/BaseTypes/GrowthInfo.hpp"
// #include "../source/TreeFunctions/TrunkFunction.hpp"
// #include "../source/TreeFunctions/BranchFunction.hpp"
// #include "../source/TreeFunctions/GrowthFunction.hpp"
// #include "../source/Meshers/BasicMesher.hpp"

// using namespace Mtree;
namespace py = pybind11;


PYBIND11_MODULE(m_tree, m) {
    m.doc() = R"pbdoc(
        Mtree plugin
        -----------------------

        .. currentmodule:: m_tree

        .. autosummary::
           :toctree: _generate

    )pbdoc";

    // py::class_<TreeFunction, std::shared_ptr<TreeFunction>>(m, "TreeFunction")
    //     .def("add_child", &TreeFunction::add_child);

    // py::class_<TrunkFunction, std::shared_ptr<TrunkFunction>, TreeFunction>(m, "TrunkFunction")
    //     .def(py::init<>())
    //     .def_readwrite("length", &TrunkFunction::length)
    //     .def_readwrite("resolution", &TrunkFunction::resolution)
    //     .def_readwrite("start_radius", &TrunkFunction::start_radius)
    //     .def_readwrite("end_radius", &TrunkFunction::end_radius)
    //     .def_readwrite("shape", &TrunkFunction::shape)
    //     .def_readwrite("up_attraction", &TrunkFunction::up_attraction)
    //     .def_readwrite("randomness", &TrunkFunction::randomness)
    //     ;
    
    // py::class_<BranchFunction, std::shared_ptr<BranchFunction>, TreeFunction>(m, "BranchFunction")
    //     .def(py::init<>())
    //     .def_readwrite("length", &BranchFunction::length)
    //     .def_readwrite("start", &BranchFunction::start)
    //     .def_readwrite("end", &BranchFunction::end)
    //     .def_readwrite("branches_density", &BranchFunction::branches_density)
    //     .def_readwrite("resolution", &BranchFunction::resolution)
    //     .def_readwrite("start_radius", &BranchFunction::start_radius)
    //     .def_readwrite("end_radius", &BranchFunction::end_radius)
    //     .def_readwrite("randomness", &BranchFunction::randomness)
    //     .def_readwrite("gravity_strength", &BranchFunction::gravity_strength)
    //     .def_readwrite("stiffness", &BranchFunction::stiffness)
    //     .def_readwrite("up_attraction", &BranchFunction::up_attraction)
    //     .def_readwrite("phillotaxis", &BranchFunction::phillotaxis)
    //     .def_readwrite("split_radius", &BranchFunction::split_radius)
    //     .def_readwrite("start_angle", &BranchFunction::start_angle)
    //     .def_readwrite("split_angle", &BranchFunction::split_angle)
    //     .def_readwrite("split_proba", &BranchFunction::split_proba)
    //     ;

    // py::class_<GrowthFunction, std::shared_ptr<GrowthFunction>, TreeFunction>(m, "GrowthFunction")
    //     .def(py::init<>())
    //     .def_readwrite("iterations", &GrowthFunction::iterations)
    //     .def_readwrite("apical_dominance", &GrowthFunction::apical_dominance)
    //     .def_readwrite("grow_threshold", &GrowthFunction::grow_threshold)
    //     .def_readwrite("cut_threshold", &GrowthFunction::cut_threshold)
    //     .def_readwrite("split_threshold", &GrowthFunction::split_threshold)
    //     .def_readwrite("split_angle", &GrowthFunction::split_angle)
    //     .def_readwrite("branch_length", &GrowthFunction::branch_length)
    //     .def_readwrite("gravitropism", &GrowthFunction::gravitropism)
    //     .def_readwrite("randomness", &GrowthFunction::randomness)
    //     .def_readwrite("gravity_strength", &GrowthFunction::gravity_strength)
    //     ;


    // py::class_<Tree>(m, "Tree")
    //     .def(py::init<>())
    //     .def("set_trunk_function", &Tree::set_first_function)
    //     .def("get_trunk_function", &Tree::get_first_function)
    //     .def("execute_functions", &Tree::execute_functions);

    // py::class_<Mesh>(m, "Mesh")
    //     .def("get_vertices", &Mesh::get_vertices)
    //     .def("get_polygons", &Mesh::get_polygons)
    //     .def("get_vertices_numpy", &Mesh::get_vertices_numpy)
    //     .def("get_polygons_numpy", &Mesh::get_polygons_numpy);


    // py::class_<TreeMesher>(m, "TreeMesher");

    // py::class_<BasicMesher>(m, "BasicMesher")
    //     .def(py::init<>())
    //     .def("mesh_tree", &BasicMesher::mesh_tree);


#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
