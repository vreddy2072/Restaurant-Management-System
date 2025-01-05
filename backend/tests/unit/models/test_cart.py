import pytest
from sqlalchemy.exc import IntegrityError
from backend.models.orm.shopping_cart import ShoppingCart, CartItem

def test_create_shopping_cart(db_session, test_user):
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()

    assert cart.id is not None
    assert cart.user_id == test_user.id
    assert cart.created_at is not None
    assert cart.updated_at is not None

def test_create_cart_item(db_session, sample_cart, sample_menu_item):
    cart_item = CartItem(
        cart_id=sample_cart.id,
        menu_item_id=sample_menu_item.id,
        quantity=1
    )
    db_session.add(cart_item)
    db_session.commit()

    assert cart_item.id is not None
    assert cart_item.quantity == 1
    assert cart_item.customizations is None

def test_cart_user_relationship(db_session, sample_cart, test_user):
    assert sample_cart.user.id == test_user.id

def test_cart_items_relationship(db_session, sample_cart, sample_cart_item):
    assert len(sample_cart.items) == 1
    assert sample_cart.items[0].id == sample_cart_item.id

def test_unique_user_cart(db_session, test_user):
    cart1 = ShoppingCart(user_id=test_user.id)
    db_session.add(cart1)
    db_session.commit()

    cart2 = ShoppingCart(user_id=test_user.id)
    db_session.add(cart2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_cart_item_with_customizations(db_session, sample_cart, sample_menu_item):
    customizations = {"notes": "Extra spicy", "toppings": ["cheese", "onions"]}
    cart_item = CartItem(
        cart_id=sample_cart.id,
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations=customizations
    )
    db_session.add(cart_item)
    db_session.commit()

    assert cart_item.customizations == customizations

def test_delete_cart_cascade_items(db_session, sample_cart, sample_cart_item):
    cart_id = sample_cart.id
    cart_item_id = sample_cart_item.id

    # Delete the cart
    db_session.delete(sample_cart)
    db_session.commit()

    # Verify cart item is also deleted
    cart_item = db_session.query(CartItem).filter_by(id=cart_item_id).first()
    assert cart_item is None
