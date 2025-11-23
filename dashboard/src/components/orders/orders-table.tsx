"use client"

import { useState, useEffect } from "react"
import { Order, getOrders } from "@/services/orders"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { format } from "date-fns"
import { Eye } from "lucide-react"

interface OrdersTableProps {
  onViewDetails: (order: Order) => void
}

export function OrdersTable({ onViewDetails }: OrdersTableProps) {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>("all")

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await getOrders()
        setOrders(data)
      } catch (error) {
        console.error("Failed to load orders:", error)
      } finally {
        setLoading(false)
      }
    }

    loadOrders()
  }, [])

  const filteredOrders = orders.filter((order) => {
    if (statusFilter === "all") return true
    return order.order_status === statusFilter
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Loading orders...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="flex items-center gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Orders</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="confirmed">Confirmed</SelectItem>
            <SelectItem value="shipped">Shipped</SelectItem>
            <SelectItem value="delivered">Delivered</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <p className="text-sm text-muted-foreground">
          {filteredOrders.length} {filteredOrders.length === 1 ? "order" : "orders"}
        </p>
      </div>

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Order #</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Items</TableHead>
              <TableHead>Total</TableHead>
              <TableHead>Payment</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Date</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredOrders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  No orders found
                </TableCell>
              </TableRow>
            ) : (
              filteredOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-medium">{order.order_number}</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{order.customer_name}</p>
                      <p className="text-xs text-muted-foreground">{order.customer_phone}</p>
                    </div>
                  </TableCell>
                  <TableCell>{order.items.length} item(s)</TableCell>
                  <TableCell>KES {order.total.toLocaleString()}</TableCell>
                  <TableCell>
                    <PaymentStatusBadge status={order.payment_status} />
                  </TableCell>
                  <TableCell>
                    <OrderStatusBadge status={order.order_status} />
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {format(new Date(order.created_at), "MMM d, yyyy")}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewDetails(order)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

function PaymentStatusBadge({ status }: { status: Order["payment_status"] }) {
  const variants = {
    completed: "default",
    pending: "secondary",
    failed: "destructive",
  } as const

  const labels = {
    completed: "Paid",
    pending: "Pending",
    failed: "Failed",
  }

  return (
    <Badge variant={variants[status]} className="capitalize">
      {labels[status]}
    </Badge>
  )
}

function OrderStatusBadge({ status }: { status: Order["order_status"] }) {
  const variants = {
    pending: "secondary",
    confirmed: "default",
    shipped: "default",
    delivered: "default",
    cancelled: "destructive",
  } as const

  return (
    <Badge variant={variants[status]} className="capitalize">
      {status}
    </Badge>
  )
}
