from dataclasses import dataclass
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
from pyomo_models.build.names import ComponentName


@dataclass
class SetDefDC:
    name: ComponentName
    index: Any = None
    within: Any = None
    initialize: Any = None
    dimen: int = 1


@dataclass
class ParamDefDC:
    name: ComponentName
    index: Any = None
    within: Any = None
    initialize: Any = None
    mutable: bool = False


@dataclass
class VarDefDC:
    name: ComponentName
    index: Any = None
    domain: Any = None
    bounds: tuple | None = None
    initialize: Any = None


@dataclass
class ConstraintDefDC:
    name: ComponentName
    index: Any = None
    rule: Callable | None = None


def test_build_helpers_accept_dataclasses_and_enums():
    model = ConcreteModel()

    set_a = SetDefDC(name=ComponentName.B, initialize=[1, 2])
    set_b = SetDefDC(name=ComponentName.G, within=set_a, initialize=[1])
    add_sets_to_instance(model, [set_a, set_b])

    assert sorted(model.B.data()) == [1, 2]
    assert sorted(model.G.data()) == [1]
    assert model.G.domain is model.B

    param_p = ParamDefDC(name=ComponentName.PD, index=set_a, initialize={1: 10, 2: 20})
    add_params_to_instance(model, [param_p])
    assert model.PD[1] == 10
    assert model.PD.index_set() is model.B

    var_x = VarDefDC(
        name=ComponentName.pG,
        index=set_a,
        domain=NonNegativeReals,
        initialize=5,
    )
    add_variables_to_instance(model, [var_x])
    assert model.pG[1].value == 5
    assert model.pG.index_set() is model.B

    def rule(m, i):
        return m.pG[i] >= m.PD[i]

    constraint_c = ConstraintDefDC(
        name=ComponentName.line_cont_realpower_max_pstve,
        index=ComponentName.B,
        rule=rule,
    )
    add_constraints_to_instance(model, [constraint_c])
    assert len(model.line_cont_realpower_max_pstve) == 2
    assert model.line_cont_realpower_max_pstve.index_set() is model.B

