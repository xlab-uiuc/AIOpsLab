from functools import wraps


def modify(method: function, namespace: str, pod_name: str = '*'):
    """
    Decorator to mark a pod in the given namespace.

    Args:
        namespace (str): The namespace of the pod.
        pod_name (str): The name of the pod.
        method (function): The method to decorate.

    Returns:
        function: The decorated method.
    """

    if not namespace:
        raise ValueError("Namespace is required.")


    @wraps(method)
    def wrapper(*args, **kwargs):
        # TODO: Implement me
        pass

    return wrapper