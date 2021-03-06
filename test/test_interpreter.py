from xcalc.interpreter import Eval
from dolfin import *
import numpy as np
import unittest


def error(true, me):
    mesh = me.function_space().mesh()
    return sqrt(abs(assemble(inner(me - true, me - true)*dx(domain=mesh))))


class TestCases(unittest.TestCase):
    '''UnitTest for (some of) xcalc.interpreter (no timeseries)'''
    def test_sanity0(self):
        mesh = UnitSquareMesh(4, 4)
        V = FunctionSpace(mesh, 'CG', 1)

        f = Expression('x[0]', degree=1)
        g = Expression('x[1]', degree=1)
        a = 3
        b = -2

        u = interpolate(f, V)
        v = interpolate(g, V)

        expr = a*u + b*v

        me = Eval(expr)
        true = Expression('a*f+b*g', f=f, g=g, a=a, b=b, degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)
        
    def test_sanity1(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'DG', 0)

        u = interpolate(Expression((('x[0]', 'x[1]'),
                                    ('2*x[0]+x[1]', 'x[0]+3*x[1]')), degree=1), T)
        expr = sym(u) + skew(u)
        me = Eval(expr)
        true = u

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity2(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)

        A = interpolate(Expression((('x[0]', 'x[1]'),
                                    ('2*x[0]+x[1]', 'x[0]+3*x[1]')), degree=1), T)
        expr = tr(sym(A) + skew(A))
        me = Eval(expr)
        true = Expression('x[0] + x[0] + 3*x[1]', degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)
        
    def test_sanity3(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)

        A = interpolate(Expression((('x[0]', 'x[1]'),
                                    ('2*x[0]+x[1]', 'x[0]+3*x[1]')), degree=1), T)
        expr = (sym(A) + skew(A))[0, 0]
        me = Eval(expr)
        true = Expression('x[0]', degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity4(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)

        A = interpolate(Expression((('x[0]', 'x[1]'),
                                    ('2*x[0]+x[1]', 'x[0]+3*x[1]')), degree=1), T)
        expr = (sym(A) + skew(A))[:, 0]
        me = Eval(expr)
        true = Expression(('x[0]', '2*x[0]+x[1]'), degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity5(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)

        A = interpolate(Expression((('1', 'x[0]'),
                                    ('2', 'x[1]')), degree=1), T)
        expr = det(A)
        me = Eval(expr)
        true = Expression('x[1]-2*x[0]', degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity6(self):
        mesh = UnitCubeMesh(5, 5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)

        A = interpolate(Expression((('x[0]', '0', '1'),
                                    ('0', '1', 'x[1]'),
                                    ('x[2]', '0', '1')), degree=1), T)
        expr = det(A)
        me = Eval(expr)
        true = Expression('x[0]-x[2]', degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity7(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)
        A = interpolate(Expression((('1', 'x[0]'),
                                    ('2', 'x[1]')), degree=1), T)

        V = VectorFunctionSpace(mesh, 'CG', 1)
        v = interpolate(Expression(('x[0]+x[1]', '1'), degree=1), V)

        me = Eval(dot(A, v))
        true = Expression(('x[1]+2*x[0]', '2*x[0]+3*x[1]'), degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity8(self):
        mesh = UnitSquareMesh(5, 5)
        T = TensorFunctionSpace(mesh, 'CG', 1)
        A = interpolate(Expression((('1', 'x[0]'),
                                    ('2', 'x[1]')), degree=1), T)

        V = VectorFunctionSpace(mesh, 'CG', 1)
        v = interpolate(Expression(('x[0]+x[1]', '1'), degree=1), V)

        me = Eval(dot(v, transpose(A)))
        true = Expression(('x[1]+2*x[0]', '2*x[0]+3*x[1]'), degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity8(self):
        mesh = UnitSquareMesh(5, 5)
    
        V = VectorFunctionSpace(mesh, 'CG', 1)
        v0 = interpolate(Expression(('x[0]+x[1]', '1'), degree=1), V)
        v1 = interpolate(Expression(('1', 'x[0]'), degree=1), V)

        me = Eval(inner(v0, v1))
        true = Expression('x[1]+2*x[0]', degree=1)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity9(self):
        mesh = UnitSquareMesh(5, 5)
        V = FunctionSpace(mesh, 'CG', 1)

        a0 = interpolate(Expression('x[0]', degree=1), V)
        a1 = interpolate(Expression('x[1]', degree=1), V)

        me = Eval(as_vector((a0, a1)))

        x, y = SpatialCoordinate(mesh)
        true = as_vector((x, y))

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_sanity10(self):
        mesh = UnitSquareMesh(5, 5)
        V = FunctionSpace(mesh, 'CG', 1)

        a0 = interpolate(Expression('x[0]', degree=1), V)
        a1 = interpolate(Expression('x[1]', degree=1), V)

        true = as_vector((as_vector((a0, a1)), as_vector((-a0, -a1))))
        me = Eval(true)

        e = error(true, me)
        self.assertTrue(e < 1E-14)
        
    def test_sanity11(self):
        mesh = UnitSquareMesh(5, 5)

        true = SpatialCoordinate(mesh)
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)


    def test_sanity12(self):
        mesh = UnitSquareMesh(5, 5)

        x, y = SpatialCoordinate(mesh)
        true = as_vector((x+y, x-y))
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_row_slice(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)
        
        A = as_matrix(((x, 2*y), (3*y, 4*x)))

        true = A[1, :]
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_col_slice(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)
        
        A = as_matrix(((x, 2*y), (3*y, 4*x)))
 
        true = A[:, 0]
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_num_vec(self):
        mesh = UnitSquareMesh(4, 4)
        r = SpatialCoordinate(mesh)
        
        true = Constant(2)*r
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_mat_vec(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)
        
        A = as_matrix(((x, 2*y), (3*y, 4*x)))

        V = VectorFunctionSpace(mesh, 'CG', 1)
        b = interpolate(Constant((1, 2)), V)
 
        true = A*b
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_mat_mat(self):
        mesh = UnitSquareMesh(4, 4)
        T = TensorFunctionSpace(mesh, 'DG', 0)
        
        A = interpolate(Constant(((1, 2), (3, 4))), T)
        B = interpolate(Constant(((1, -2), (-1, 4))), T)

        true = A*B
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_mat_mat_mat(self):
        mesh = UnitSquareMesh(4, 4)
        T = TensorFunctionSpace(mesh, 'DG', 0)
        
        A = interpolate(Constant(((1, 2), (3, 4))), T)
        B = interpolate(Constant(((1, -2), (-1, 4))), T)

        true = A*B*A
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)


    def test_comp_tensor_mat_mat_vec(self):
        mesh = UnitSquareMesh(4, 4)
        
        T = TensorFunctionSpace(mesh, 'DG', 0)        
        A = interpolate(Constant(((1, 2), (3, 4))), T)
        B = interpolate(Constant(((1, -2), (-1, 4))), T)

        V = VectorFunctionSpace(mesh, 'DG', 0)
        b = interpolate(Constant((-1, -2)), V)

        true = A*B*b
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_comp_tensor_num_mat(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)

        A = as_matrix(((x, y), (y, -x)))
        
        true = Constant(2)*A
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_min(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)
        
        true = Min(x, y)
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_max(self):
        mesh = UnitSquareMesh(4, 4)
        x, y = SpatialCoordinate(mesh)
        
        true = Max(x+y, 2*y)
        me = Eval(true)
        
        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_cond_simple_conv(self):
        # Outside of CG1 with nonlinearity?
        errors = []
        for n in (4, 8, 16, 32, 64):
            mesh = UnitSquareMesh(n, n)
            x, y = SpatialCoordinate(mesh)
            true = conditional(x < y, x+y, x-y)
        
            me = Eval(true)
            errors.append(error(true, me))
        self.assertTrue((np.diff(errors) < 0).all())

    def test_cond_simple(self):
        mesh = UnitSquareMesh(4, 4)
        V = FunctionSpace(mesh, 'DG', 0)

        x = interpolate(Constant(1), V)
        y = interpolate(Constant(2), V)

        true = conditional(x < y, x+y, x-y)        
        me = Eval(true)

        e = error(true, me)
        self.assertTrue(e < 1E-14)

    def test_cond_logic(self):
        errors = []
        for n in (4, 8, 16, 32, 64):
            mesh = UnitSquareMesh(n, n)
            x, y = SpatialCoordinate(mesh)
            true = conditional(And(x < y, Constant(0) < x), x+y, x-y)
        
            me = Eval(true)
            errors.append(error(true, me))
        self.assertTrue((np.diff(errors) < 0).all())

    def test_cond_logic_simple(self):
        # We're outside of the CG1!
        mesh = UnitSquareMesh(4, 4)
        V = FunctionSpace(mesh, 'DG', 0)

        x = interpolate(Constant(1), V)
        y = interpolate(Constant(2), V)

        true = conditional(And(x < y, 0 < x), x+y, x-y)        
        me = Eval(true)

        e = error(true, me)
        self.assertTrue(e < 1E-14)
