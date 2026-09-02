from .models import Cart


def cart_context(request):

    cart_count = 0

    if request.user.is_authenticated:

        try:
            cart = request.user.customer_profile.cart
            cart_count = cart.total_items

        except Exception:
            cart_count = 0

    return {
        'cart_count': cart_count,
    }