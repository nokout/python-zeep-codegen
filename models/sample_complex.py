from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "http://example.com/order"


@dataclass(kw_only=True)
class AddressType:
    street: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    city: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    state: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    postal_code: str = field(
        metadata={
            "name": "postalCode",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    country: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )


@dataclass(kw_only=True)
class ContactType:
    email: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    phone: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    mobile: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )


@dataclass(kw_only=True)
class MetadataEntryType:
    key: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    value: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )


class OrderStatusType(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(kw_only=True)
class ProductType:
    product_id: str = field(
        metadata={
            "name": "productId",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    price: Decimal = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    category: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    tags: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    sku: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    in_stock: bool = field(
        default=True,
        metadata={
            "name": "inStock",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class ShippingType:
    carrier: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    tracking_number: None | str = field(
        default=None,
        metadata={
            "name": "trackingNumber",
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    estimated_delivery: None | XmlDate = field(
        default=None,
        metadata={
            "name": "estimatedDelivery",
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    actual_delivery: None | XmlDate = field(
        default=None,
        metadata={
            "name": "actualDelivery",
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    shipping_cost: Decimal = field(
        metadata={
            "name": "shippingCost",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )


@dataclass(kw_only=True)
class CustomerType:
    customer_id: str = field(
        metadata={
            "name": "customerId",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    contact: ContactType = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    billing_address: AddressType = field(
        metadata={
            "name": "billingAddress",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    shipping_address: None | AddressType = field(
        default=None,
        metadata={
            "name": "shippingAddress",
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )


@dataclass(kw_only=True)
class MetadataType:
    entry: list[MetadataEntryType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )


@dataclass(kw_only=True)
class OrderItemType:
    product: ProductType = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    quantity: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    unit_price: Decimal = field(
        metadata={
            "name": "unitPrice",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    discount: None | Decimal = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    subtotal: Decimal = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )


@dataclass(kw_only=True)
class PaymentType:
    method: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    transaction_id: None | str = field(
        default=None,
        metadata={
            "name": "transactionId",
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    amount: Decimal = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    currency: str = field(
        default="USD",
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        },
    )
    metadata: None | MetadataType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )


@dataclass(kw_only=True)
class OrderType:
    order_id: str = field(
        metadata={
            "name": "orderId",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    order_date: XmlDateTime = field(
        metadata={
            "name": "orderDate",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    status: OrderStatusType = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    customer: CustomerType = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    items: list[OrderItemType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "min_occurs": 1,
        },
    )
    payment: PaymentType = field(
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    shipping: None | ShippingType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    notes: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://example.com/order",
        },
    )
    total_amount: Decimal = field(
        metadata={
            "name": "totalAmount",
            "type": "Element",
            "namespace": "http://example.com/order",
            "required": True,
        }
    )
    version: str = field(
        init=False,
        default="1.0",
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Order(OrderType):
    class Meta:
        namespace = "http://example.com/order"
