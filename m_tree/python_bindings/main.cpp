#include <iostream>
#include <exception>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "source/mesh/Mesh.hpp"
#include "source/tree/Tree.hpp"
#include "source/tree_functions/base_types/Property.hpp"
#include "source/tree_functions/TrunkFunction.hpp"
#include "source/tree_functions/BranchFunction.hpp"
#include "source/tree_functions/GrowthFunction.hpp"
#include "source/meshers/splines_mesher/BasicMesher.hpp"
#include "source/meshers/manifold_mesher/ManifoldMesher.hpp"


using namespace Mtree;
namespace py = pybind11;


PYBIND11_MODULE(m_tree, m) {
    m.doc() = R"pbdoc(
        Mtree plugin
        -----------------------

        .. currentmodule:: m_tree

        .. autosummary::
           :toctree: _generate

    )pbdoc";

    py::class_<TreeFunction, std::shared_ptr<TreeFunction>>(m, "TreeFunction")
        .def("add_child", &TreeFunction::add_child);

    py::class_<ConstantProperty, std::shared_ptr<ConstantProperty>>(m, "ConstantProperty")
        .def(py::init<>())
        .def(py::init<float, float, float>())
        .def_readwrite("min", &ConstantProperty::min)
        .def_readwrite("max", &ConstantProperty::max)
        .def_readwrite("value", &ConstantProperty::value)
        ;

    py::class_<RandomProperty, std::shared_ptr<RandomProperty>>(m, "RandomProperty")
        .def(py::init<>())
        .def_readwrite("min", &RandomProperty::min_value)
        .def_readwrite("max", &RandomProperty::max_value)
        ;

    py::class_<SimpleCurveProperty, std::shared_ptr<SimpleCurveProperty>>(m, "SimpleCurveProperty")
        .def(py::init<>())
        .def_readwrite("x_min", &SimpleCurveProperty::x_min)
        .def_readwrite("y_min", &SimpleCurveProperty::y_min)
        .def_readwrite("x_max", &SimpleCurveProperty::x_max)
        .def_readwrite("y_max", &SimpleCurveProperty::y_max)
        .def_readwrite("power", &SimpleCurveProperty::power)
        ;

    py::class_<PropertyWrapper, std::shared_ptr<PropertyWrapper>>(m, "PropertyWrapper")
        .def(py::init<>())
        .def(py::init<ConstantProperty&>())
        .def(py::init<RandomProperty&>())
        .def(py::init<SimpleCurveProperty&>())
        .def("set_constant_property", &PropertyWrapper::set_property<ConstantProperty>)
        .def("set_random_property", &PropertyWrapper::set_property<RandomProperty>)
        .def("set_simple_curve_property", &PropertyWrapper::set_property<SimpleCurveProperty>)
        ;

    py::class_<TrunkFunction, std::shared_ptr<TrunkFunction>, TreeFunction>(m, "TrunkFunction")
        .def(py::init<>())
        .def_readwrite("length", &TrunkFunction::length)
        .def_readwrite("resolution", &TrunkFunction::resolution)
        .def_readwrite("start_radius", &TrunkFunction::start_radius)
        .def_readwrite("end_radius", &TrunkFunction::end_radius)
        .def_readwrite("shape", &TrunkFunction::shape)
        .def_readwrite("up_attraction", &TrunkFunction::up_attraction)
        .def_readwrite("randomness", &TrunkFunction::randomness)
        ;
    
    py::class_<BranchFunction, std::shared_ptr<BranchFunction>, TreeFunction>(m, "BranchFunction")
        .def(py::init<>())
        .def_readwrite("length", &BranchFunction::length)
        .def_readwrite("start", &BranchFunction::start)
        .def_readwrite("end", &BranchFunction::end)
        .def_readwrite("branches_density", &BranchFunction::branches_density)
        .def_readwrite("resolution", &BranchFunction::resolution)
        .def_readwrite("break_chance", &BranchFunction::break_chance)
        .def_readwrite("start_radius", &BranchFunction::start_radius)
        .def_readwrite("end_radius", &BranchFunction::end_radius)
        .def_readwrite("randomness", &BranchFunction::randomness)
        .def_readwrite("flatness", &BranchFunction::flatness)
        .def_readwrite("gravity_strength", &BranchFunction::gravity_strength)
        .def_readwrite("stiffness", &BranchFunction::stiffness)
        .def_readwrite("up_attraction", &BranchFunction::up_attraction)
        .def_readwrite("phillotaxis", &BranchFunction::phillotaxis)
        .def_readwrite("split_radius", &BranchFunction::split_radius)
        .def_readwrite("start_angle", &BranchFunction::start_angle)
        .def_readwrite("split_angle", &BranchFunction::split_angle)
        .def_readwrite("split_proba", &BranchFunction::split_proba)
        ;

    py::class_<GrowthFunction, std::shared_ptr<GrowthFunction>, TreeFunction>(m, "GrowthFunction")
        .def(py::init<>())
        .def_readwrite("iterations", &GrowthFunction::iterations)
        .def_readwrite("apical_dominance", &GrowthFunction::apical_dominance)
        .def_readwrite("grow_threshold", &GrowthFunction::grow_threshold)
        .def_readwrite("cut_threshold", &GrowthFunction::cut_threshold)
        .def_readwrite("split_threshold", &GrowthFunction::split_threshold)
        .def_readwrite("split_angle", &GrowthFunction::split_angle)
        .def_readwrite("branch_length", &GrowthFunction::branch_length)
        .def_readwrite("gravitropism", &GrowthFunction::gravitropism)
        .def_readwrite("randomness", &GrowthFunction::randomness)
        .def_readwrite("gravity_strength", &GrowthFunction::gravity_strength)
        ;


    py::class_<Tree>(m, "Tree")
        .def(py::init<>())
        .def("set_trunk_function", &Tree::set_first_function)
        .def("get_trunk_function", &Tree::get_first_function)
        .def("execute_functions", &Tree::execute_functions);

    py::class_<Mesh>(m, "Mesh")
        .def("get_vertices", [](const Mesh& mesh)
            {
        	    py::array_t<float> result(mesh.vertices.size() * 3);
			    py::buffer_info buff = result.request();

			    float* ptr = (float*)buff.ptr;
			    for (int i = 0; i < mesh.vertices.size(); i++)
			    {
				    for (size_t j = 0; j < 3; j++)
				    {
					    ptr[i*3+j] = mesh.vertices[i][j];
				    }
			    }

			    return result;
            })
        .def("get_float_attribute", [](const Mesh& mesh, std::string name)
            {
                if (mesh.attributes.count(name) == 0)
                {
                    throw std::invalid_argument("attribute " + name + " doesn't exist");
                }
                auto& attribute = *static_cast<Attribute<float>*>(mesh.attributes.at(name).get());
                py::array_t<float> result(mesh.vertices.size());
                py::buffer_info buff = result.request();

                float* ptr = (float*)buff.ptr;
                for (int i = 0; i < mesh.vertices.size(); i++)
                {
                    ptr[i] = attribute.data[i];
                }
                return result;
            })
        .def("get_polygons", [](const Mesh& mesh) 
            {
                py::array_t<int> result(mesh.polygons.size() * 4);
             	py::buffer_info buff = result.request();

             	int* ptr = (int*)buff.ptr;
             	for (int i = 0; i < mesh.polygons.size(); i++)
             	{
             		for (int j = 0; j < 4; j++)
             		{
             			ptr[i * 4 + j] = mesh.polygons[i][j];
             		}
             	}
             	return result;
            });


    py::class_<TreeMesher>(m, "TreeMesher");

    py::class_<BasicMesher>(m, "BasicMesher")
        .def(py::init<>())
        .def("mesh_tree", &BasicMesher::mesh_tree);
    
    py::class_<ManifoldMesher>(m, "ManifoldMesher")
        .def(py::init<>())
        .def_readwrite("radial_n_points", &ManifoldMesher::radial_resolution)
        .def("mesh_tree", &ManifoldMesher::mesh_tree);


#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
