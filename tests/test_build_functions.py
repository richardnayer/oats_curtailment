from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

import pytest

pytest.importorskip("pyomo")
from pyomo.environ import ConcreteModel, NonNegativeReals

from pyomo_models.build.functions import (
    add_constraints_to_instance,
    add_params_to_instance,
    add_sets_to_instance,
    add_variables_to_instance,
)


class Names(Enum):
    A = "A"
    B = "B"
    P = "P"
    X = "X"
    C = "C"


@dataclass
class SetDefDC:
    name: Names
    index: Any = None
    within: Any = None
    initialize: Any = None
    dimen: int = 1


@dataclass
class ParamDefDC:
    name: Names
    index: Any = None
    within: Any = None
    initialize: Any = None
    mutable: bool = False


@dataclass
class VarDefDC:
    name: Names
    index: Any = None
    domain: Any = None
    bounds: tuple | None = None
    initialize: Any = None


@dataclass
class ConstraintDefDC:
    name: Names
    index: Any = None
    rule: Callable | None = None


def test_build_helpers_accept_dataclasses_and_enums():
    model = ConcreteModel()

    set_a = SetDefDC(name=Names.A, initialize=[1, 2])
    set_b = SetDefDC(name=Names.B, within=set_a, initialize=[1])
    add_sets_to_instance(model, [set_a, set_b])

    assert sorted(model.A.data()) == [1, 2]
    assert sorted(model.B.data()) == [1]
    assert model.B.domain is model.A

    param_p = ParamDefDC(name=Names.P, index=set_a, initialize={1: 10, 2: 20})
    add_params_to_instance(model, [param_p])
    assert model.P[1] == 10
    assert model.P.index_set() is model.A

    var_x = VarDefDC(
        name=Names.X,
        index=set_a,
        domain=NonNegativeReals,
        initialize=5,
    )
    add_variables_to_instance(model, [var_x])
    assert model.X[1].value == 5
    assert model.X.index_set() is model.A

    def rule(m, i):
        return m.X[i] >= m.P[i]

    constraint_c = ConstraintDefDC(name=Names.C, index=Names.A, rule=rule)
    add_constraints_to_instance(model, [constraint_c])
    assert len(model.C) == 2
    assert model.C.index_set() is model.A

