"use client"

import { useState } from "react"
import { Order } from "@/services/orders"
import { OrdersTable } from "@/components/orders/orders-table"
import { OrderDetails } from "@/components/orders/order-details"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function OrdersPage() {
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  function handleViewDetails(order: Order) {
    setSelectedOrder(order)
    setDetailsOpen(true)
  }

  function handleDetailsClose() {
    setDetailsOpen(false)
    setSelectedOrder(null)
  }

  function handleStatusUpdate() {
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <Card>
        <CardHeader>
          <CardTitle>Orders</CardTitle>
          <CardDescription>
            Manage customer orders, track payments, and update delivery status.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <OrdersTable key={refreshKey} onViewDetails={handleViewDetails} />
        </CardContent>
      </Card>

      <OrderDetails
        order={selectedOrder}
        open={detailsOpen}
        onClose={handleDetailsClose}
        onStatusUpdate={handleStatusUpdate}
      />
    </div>
  )
}
