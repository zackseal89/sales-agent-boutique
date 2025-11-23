"use client"

import { useState } from "react"
import { Customer } from "@/services/customers"
import { CustomerList } from "@/components/customers/customer-list"
import { CustomerProfile } from "@/components/customers/customer-profile"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function CustomersPage() {
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [profileOpen, setProfileOpen] = useState(false)

  function handleViewProfile(customer: Customer) {
    setSelectedCustomer(customer)
    setProfileOpen(true)
  }

  function handleProfileClose() {
    setProfileOpen(false)
    setSelectedCustomer(null)
  }

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <Card>
        <CardHeader>
          <CardTitle>Customers</CardTitle>
          <CardDescription>
            View and manage your customer database. Track purchase history and preferences.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CustomerList onViewProfile={handleViewProfile} />
        </CardContent>
      </Card>

      <CustomerProfile
        customerId={selectedCustomer?.id || null}
        open={profileOpen}
        onClose={handleProfileClose}
      />
    </div>
  )
}
