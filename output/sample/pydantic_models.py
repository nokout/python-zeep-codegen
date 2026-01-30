"""
Generated Pydantic Models

Auto-generated from module: generated_dataclasses.sample
Do not edit manually.
"""

from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from generated_dataclasses.sample import *

class CustomerType(BaseModel):
    customer_id: <class 'str'>
    name: <class 'str'>
    email: <class 'str'>

class ItemListType(BaseModel):
    item: list[utils.conversion.ItemType] = <class 'list'>

class ItemType(BaseModel):
    product_id: <class 'str'>
    quantity: <class 'int'>
    price: <class 'decimal.Decimal'>

class OrderRequest(BaseModel):
    order_id: <class 'str'>
    customer: <class 'utils.conversion.CustomerType'>
    items: <class 'utils.conversion.ItemListType'>

class OrderRequestType(BaseModel):
    order_id: <class 'str'>
    customer: <class 'utils.conversion.CustomerType'>
    items: <class 'utils.conversion.ItemListType'>

class OrderResponse(BaseModel):
    order_id: <class 'str'>
    status: <class 'str'>
    timestamp: <class 'xsdata.models.datatype.XmlDateTime'>

class OrderResponseType(BaseModel):
    order_id: <class 'str'>
    status: <class 'str'>
    timestamp: <class 'xsdata.models.datatype.XmlDateTime'>

