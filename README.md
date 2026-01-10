<div align="center"><img src="https://github.com/user-attachments/assets/5a719726-1a8e-4579-97ac-604bad64b184" width="256" align="center"></div>

## Concepts
Foxhound is a cheap knockoff of the JVM Spring framework.  
Instead of Beans, we define Components (which are also a Spring concept but creativity is hard).  
Components are basically objects - instances of classes. Components can depend on Components.  
All Components are stored in a pool called Container.  
When wiring (injecting) a dependency of type T, Foxhound will simply check its Container to try and pull a Component of kind T.  
Multiple Components of the same type can exist in the same Container. To select a specific Component, we use qualifiers.  
So, each Component has a _kind_ and an optional _qualifier_.  
Different Components of the same kind can't share a qualifier.  

## Usage
To define a Component we can use the `component` decorator on both classes and functions:
- If used on a function, the dependencies and kind will be inferred entirely from type annotations (arguments and return type), and for this exact reason they are mandatory.
- If used on a class, the dependencies will be inferred similarly from the constructor, and the kind from the class itself.

To use Components as dependencies without defining a new one we can use the `wire` decorator (functions only).

Initialize the DI process via the `start` function.

**Simple example:**
```python
from foxhound import component, start, wire


@component()
class Agent:
    def __init__(self, codename: str):
        self.codename = codename


@component()
def name() -> str:
    return 'Snake'


@wire()
def call_agent(agent: Agent) -> None:
    print(f'{agent.codename}, do you copy?')


if __name__ == '__main__':
    start()
    call_agent()
```
```
Snake, do you copy?
```

Qualifiers are used to distinguish between Components of the same type.  
Use `component`'s `qualifier` parameter to define the Component's qualifier.  
Use the `param_qualifier` parameter (of both `component` and `wire`) to select Components by a qualifier: pass a dictionary containing the name of the parameter as a key to the desired qualifier.

**Qualifier example:**
```python
from foxhound import component, start, wire


@component(qualifier='major_zero')
def saved_frequency_a() -> float:
    return 140.85


@component(qualifier='eva')
def saved_frequency_a() -> float:
    return 142.52


@wire(param_qualifiers={'frequency': 'major_zero'})
def radio_call(frequency: float) -> None:
    print(f'SEND {frequency}')


if __name__ == '__main__':
    start()
    radio_call()
```
```
SEND 140.85
```

## How It Works
When a class or a function is decorated as `component`, a Component Definition is registered. These define how to inflate the Component (a function with parameter qualifiers, if any), alongside some metadata (its own qualifier and kind).  
All these Component Definitions form a queue of inflation tasks. The queue is iterated, and each task is attempted - if the dependencies can be satisfied (== exist in the Container), the Component is created, added to the Container, and removed from the queue. If the queue hasn't changed throughout the entire iteration - a dependency is missing (or circular).  

For example, for definitions:  
```UserService (depends on DbService, Logger), DbService (no dependencies), Logger (no dependencies)```
Wiring would look like so:
```
--- Iteration #1 ---
> UserService - failed, 2 dependencies, container is empty
> DbService - success, no dependencies, added to container
> Logger - success, no dependencies, added to container
Progress? true

--- Iteration #2 ---
> UserService - success, 2 dependencies, container contains both
Progress? true
```

This method is very simple, yet not very efficient. All dependencies are declared in advanced, meaning they could be mapped into a graph, iterable much more efficiently (but not enough to get my lazy ass to actually implement it).

### Meta-Definition
This section is here because meta-definitions shouldn't be used without a good grasp of the wiring process. If a Component is of kind Component Definition it would be inflated just like any other component, except its value would enter the inflation task queue rather than the Container. At it's current state - pretty useless and can create wiring issues, but acts as a foundation to potential 0-N Components from a single definition.
