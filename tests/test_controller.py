import pytest
from ninja_extra.permissions.common import AllowAny
from ninja_extra.controllers.base import MissingRouterDecoratorException
from ninja_extra import APIController, route, router, NinjaExtraAPI
from ninja_extra.controllers.router import ControllerRouter
from ninja_extra.controllers import RouteFunction


class SomeController(APIController):
    pass


class SomeControllerWithInject(APIController):
    def __init__(self, a: str):
        pass


class SomeControllerWithRoute(APIController):
    @route.get('/example')
    def example(self):
        pass

    @route.get('/example/{ex_id}')
    def example2(self, ex_id: str):
        pass


@router("", tags=['new tag'])
class SomeControllerWithRouter(APIController):
    @route.get('/example')
    def example(self):
        pass

    @route.get('/example/{ex_id}')
    def example2(self, ex_id: str):
        pass


class TestAPIController:
    def test_controller_should_have_preset_properties(self):
        api = NinjaExtraAPI()
        assert SomeController.tags == ['some']
        assert SomeController._path_operations == {}
        assert SomeController.permission_classes is None
        assert SomeController._router is None
        assert SomeController.api is None
        assert SomeController.registered is False

        with pytest.raises(MissingRouterDecoratorException) as ex:
            api.register_controllers(SomeController)
        assert 'Could not register controller' in str(ex.value)

    def test_controller_with_router_should_have_preset_properties(self):
        api = NinjaExtraAPI()
        assert SomeControllerWithRouter.permission_classes == [AllowAny]
        assert isinstance(SomeControllerWithRouter._router, ControllerRouter)
        assert SomeControllerWithRouter.api is None
        assert SomeControllerWithRouter.registered is False

        api.register_controllers(SomeControllerWithRouter)
        assert SomeControllerWithRouter.api == api
        assert SomeControllerWithRouter.registered

    def test_controller_should_wrap_with_inject(self):
        assert not hasattr(SomeController.__init__, '__bindings__')
        assert hasattr(SomeControllerWithInject.__init__, '__bindings__')

    def test_controller_should_have_path_operation_list(self):
        assert len(SomeControllerWithRoute._path_operations) == 2

        route_function: RouteFunction = SomeControllerWithRoute.example
        path_view = SomeControllerWithRoute._path_operations.get(str(route_function))
        assert path_view, 'route doesnt exist in controller'
        assert len(path_view.operations) == 1

        operation = path_view.operations[0]
        assert operation.methods == route_function.route_definition.route_params.methods
        assert operation.operation_id == route_function.route_definition.route_params.operation_id

    def test_controller_route_function_should_know_their_controller(self):
        assert len(SomeControllerWithRoute._path_operations) == 2
        for route_function in SomeControllerWithRoute.get_route_functions():
            assert route_function.controller == SomeControllerWithRoute