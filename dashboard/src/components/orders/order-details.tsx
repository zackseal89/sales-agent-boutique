"use client"

import { Order, updateOrderStatus } from "@/services/orders"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { format } from "date-fns"
import { Package, MapPin, CreditCard, User, Phone } from "lucide-react"
import { useState } from "react"

interface OrderDetailsProps {
  order: Order | null
  open: boolean
  onClose: () => void
  onStatusUpdate?: () => void
}

export function OrderDetails({ order, open, onClose, onStatusUpdate }: OrderDetailsProps) {
  const [updating, setUpdating] = useState(false)

  if (!order) return null

  async function handleStatusChange(newStatus: Order["order_status"]) {
    setUpdating(true)
    try {
      await updateOrderStatus(order.id, newStatus)
      onStatusUpdate?.()
    } catch (error) {
      console.error("Failed to update order status:", error)
    } finally {
      setUpdating(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Order Details</DialogTitle>
          <DialogDescription>Order #{order.order_number}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Customer Information */}
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <User className="h-4 w-4" />
              Customer Information
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Name:</span>
                <span className="font-medium">{order.customer_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Phone:</span>
                <span className="font-medium">{order.customer_phone}</span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Order Items */}
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Package className="h-4 w-4" />
              Order Items
            </h3>
            <div className="space-y-3">
              {order.items.map((item) => (
                <div key={item.id} className="flex gap-3 border rounded-lg p-3">
                  <img
                    src={item.product_image}
                    alt={item.product_name}
                    className="w-16 h-16 object-cover rounded"
                  />
                  <div className="flex-1">
                    <p className="font-medium">{item.product_name}</p>
                    <div className="flex gap-2 mt-1">
                      {item.size && (
                        <Badge variant="outline" className="text-xs">
                          Size: {item.size}
                        </Badge>
                      )}
                      {item.color && (
                        <Badge variant="outline" className="text-xs">
                          Color: {item.color}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Qty: {item.quantity} × KES {item.price.toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">
                      KES {(item.quantity * item.price).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Payment Information */}
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Payment Information
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subtotal:</span>
                <span>KES {order.subtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delivery Fee:</span>
                <span>KES {order.delivery_fee.toLocaleString()}</span>
              </div>
              <Separator />
              <div className="flex justify-between font-semibold">
                <span>Total:</span>
                <span>KES {order.total.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center pt-2">
                <span className="text-muted-foreground">Payment Status:</span>
                <Badge
                  variant={
                    order.payment_status === "completed"
                      ? "default"
                      : order.payment_status === "pending"
                      ? "secondary"
                      : "destructive"
                  }
                >
                  {order.payment_status}
                </Badge>
              </div>
              {order.mpesa_transaction_id && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">M-Pesa Transaction:</span>
                  <span className="font-mono text-xs">{order.mpesa_transaction_id}</span>
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Delivery Information */}
          <div>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Delivery Information
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Address:</span>
                <span className="font-medium text-right">{order.delivery_address}</span>
              </div>
              {order.delivery_notes && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Notes:</span>
                  <span className="text-right">{order.delivery_notes}</span>
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Order Status */}
          <div>
            <h3 className="font-semibold mb-3">Order Status</h3>
            <div className="flex items-center gap-3">
              <Select
                value={order.order_status}
                onValueChange={handleStatusChange}
                disabled={updating}
              >
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
              {updating && <span className="text-sm text-muted-foreground">Updating...</span>}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Created: {format(new Date(order.created_at), "PPpp")}
            </p>
            <p className="text-xs text-muted-foreground">
              Updated: {format(new Date(order.updated_at), "PPpp")}
            </p>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
