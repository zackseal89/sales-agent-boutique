"use client"

import { useEffect, useState } from "react"
import { CustomerDetail, getCustomer } from "@/services/customers"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { format } from "date-fns"
import { User, Phone, Mail, ShoppingBag, Heart, Ruler, Palette } from "lucide-react"

interface CustomerProfileProps {
  customerId: string | null
  open: boolean
  onClose: () => void
}

export function CustomerProfile({ customerId, open, onClose }: CustomerProfileProps) {
  const [customer, setCustomer] = useState<CustomerDetail | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function loadCustomer() {
      if (!customerId) return

      setLoading(true)
      try {
        const data = await getCustomer(customerId)
        setCustomer(data)
      } catch (error) {
        console.error("Failed to load customer:", error)
      } finally {
        setLoading(false)
      }
    }

    if (open && customerId) {
      loadCustomer()
    }
  }, [customerId, open])

  if (!customer && !loading) return null

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Customer Profile</DialogTitle>
          <DialogDescription>View customer details and purchase history</DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <p className="text-sm text-muted-foreground">Loading customer...</p>
          </div>
        ) : customer ? (
          <div className="space-y-6">
            {/* Contact Information */}
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <User className="h-4 w-4" />
                Contact Information
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{customer.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{customer.phone}</span>
                </div>
                {customer.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{customer.email}</span>
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Purchase Summary */}
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <ShoppingBag className="h-4 w-4" />
                Purchase Summary
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground mb-1">Total Orders</p>
                  <p className="text-2xl font-bold">{customer.total_orders}</p>
                </div>
                <div className="border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground mb-1">Total Spent</p>
                  <p className="text-2xl font-bold">
                    KES {customer.total_spent.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            <Separator />

            {/* Preferences */}
            {customer.preferences && (
              <>
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Heart className="h-4 w-4" />
                    Preferences
                  </h3>
                  <div className="space-y-3">
                    {customer.preferences.favorite_categories && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">
                          Favorite Categories:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {customer.preferences.favorite_categories.map((category) => (
                            <Badge key={category} variant="secondary">
                              {category}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {customer.preferences.preferred_sizes && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-2 flex items-center gap-1">
                          <Ruler className="h-3 w-3" />
                          Preferred Sizes:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {customer.preferences.preferred_sizes.map((size) => (
                            <Badge key={size} variant="outline">
                              {size}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {customer.preferences.preferred_colors && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-2 flex items-center gap-1">
                          <Palette className="h-3 w-3" />
                          Preferred Colors:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {customer.preferences.preferred_colors.map((color) => (
                            <Badge key={color} variant="outline">
                              {color}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <Separator />
              </>
            )}

            {/* Notes */}
            {customer.notes && (
              <>
                <div>
                  <h3 className="font-semibold mb-2">Notes</h3>
                  <p className="text-sm text-muted-foreground">{customer.notes}</p>
                </div>
                <Separator />
              </>
            )}

            {/* Order History */}
            <div>
              <h3 className="font-semibold mb-3">Order History</h3>
              <div className="space-y-2">
                {customer.orders.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No orders yet</p>
                ) : (
                  customer.orders.map((order) => (
                    <div
                      key={order.id}
                      className="flex items-center justify-between border rounded-lg p-3"
                    >
                      <div>
                        <p className="font-medium text-sm">{order.order_number}</p>
                        <p className="text-xs text-muted-foreground">
                          {format(new Date(order.created_at), "MMM d, yyyy")}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-sm">
                          KES {order.total.toLocaleString()}
                        </p>
                        <Badge variant="secondary" className="text-xs capitalize">
                          {order.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Customer since: {format(new Date(customer.created_at), "PPP")}</p>
              <p>Last interaction: {format(new Date(customer.last_interaction), "PPP")}</p>
            </div>
          </div>
        ) : null}

        <div className="flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
