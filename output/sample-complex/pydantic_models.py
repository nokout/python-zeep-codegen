"""
Generated Pydantic Models

Auto-generated from module: generated_dataclasses.sample_complex
Do not edit manually.
"""

from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from generated_dataclasses.sample_complex import *

class AddressType(BaseModel):
    street: <class 'str'>
    city: <class 'str'>
    state: <class 'str'>
    postal_code: <class 'str'>
    country: <class 'str'>

class ContactType(BaseModel):
    email: <class 'str'>
    phone: None | str = None
    mobile: None | str = None

class CustomerType(BaseModel):
    customer_id: <class 'str'>
    name: <class 'str'>
    contact: <class 'utils.conversion.ContactType'>
    billing_address: <class 'utils.conversion.AddressType'>
    shipping_address: None | utils.conversion.AddressType = None

class MetadataEntryType(BaseModel):
    key: <class 'str'>
    value: <class 'str'>

class MetadataType(BaseModel):
    entry: list[utils.conversion.MetadataEntryType] = <class 'list'>

class Order(BaseModel):
    order_id: <class 'str'>
    order_date: <class 'xsdata.models.datatype.XmlDateTime'>
    status: <enum 'OrderStatusType'>
    customer: <class 'utils.conversion.CustomerType'>
    items: list[utils.conversion.OrderItemType] = <class 'list'>
    payment: <class 'utils.conversion.PaymentType'>
    shipping: None | utils.conversion.ShippingType = None
    notes: None | str = None
    total_amount: <class 'decimal.Decimal'>
    version: <class 'str'> = '1.0'

class OrderItemType(BaseModel):
    product: <class 'utils.conversion.ProductType'>
    quantity: <class 'int'>
    unit_price: <class 'decimal.Decimal'>
    discount: None | decimal.Decimal = None
    subtotal: <class 'decimal.Decimal'>

class OrderType(BaseModel):
    order_id: <class 'str'>
    order_date: <class 'xsdata.models.datatype.XmlDateTime'>
    status: <enum 'OrderStatusType'>
    customer: <class 'utils.conversion.CustomerType'>
    items: list[utils.conversion.OrderItemType] = <class 'list'>
    payment: <class 'utils.conversion.PaymentType'>
    shipping: None | utils.conversion.ShippingType = None
    notes: None | str = None
    total_amount: <class 'decimal.Decimal'>
    version: <class 'str'> = '1.0'

class PaymentType(BaseModel):
    method: <class 'str'>
    transaction_id: None | str = None
    amount: <class 'decimal.Decimal'>
    currency: <class 'str'> = 'USD'
    metadata: None | utils.conversion.MetadataType = None

class ProductType(BaseModel):
    product_id: <class 'str'>
    name: <class 'str'>
    description: None | str = None
    price: <class 'decimal.Decimal'>
    category: <class 'str'>
    tags: list[str] = <class 'list'>
    sku: <class 'str'>
    in_stock: <class 'bool'> = True

class ShippingType(BaseModel):
    carrier: <class 'str'>
    tracking_number: None | str = None
    estimated_delivery: None | xsdata.models.datatype.XmlDate = None
    actual_delivery: None | xsdata.models.datatype.XmlDate = None
    shipping_cost: <class 'decimal.Decimal'>

