"use client"

import { useState, useEffect } from "react"
import { Customer, getCustomers, searchCustomers } from "@/services/customers"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { format } from "date-fns"
import { Eye, Search } from "lucide-react"

interface CustomerListProps {
  onViewProfile: (customer: Customer) => void
}

export function CustomerList({ onViewProfile }: CustomerListProps) {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    async function loadCustomers() {
      try {
        const data = await getCustomers()
        setCustomers(data)
      } catch (error) {
        console.error("Failed to load customers:", error)
      } finally {
        setLoading(false)
      }
    }

    loadCustomers()
  }, [])

  async function handleSearch() {
    if (!searchQuery.trim()) {
      // Reload all customers
      setSearching(true)
      try {
        const data = await getCustomers()
        setCustomers(data)
      } catch (error) {
        console.error("Failed to load customers:", error)
      } finally {
        setSearching(false)
      }
      return
    }

    setSearching(true)
    try {
      const results = await searchCustomers(searchQuery)
      setCustomers(results)
    } catch (error) {
      console.error("Failed to search customers:", error)
    } finally {
      setSearching(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Loading customers...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, phone, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="pl-9"
          />
        </div>
        <Button onClick={handleSearch} disabled={searching}>
          {searching ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Customer</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>Email</TableHead>
              <TableHead className="text-right">Total Orders</TableHead>
              <TableHead className="text-right">Total Spent</TableHead>
              <TableHead>Last Interaction</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {customers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  {searchQuery ? "No customers found" : "No customers yet"}
                </TableCell>
              </TableRow>
            ) : (
              customers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell className="font-medium">{customer.name}</TableCell>
                  <TableCell className="text-sm">{customer.phone}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {customer.email || "-"}
                  </TableCell>
                  <TableCell className="text-right">{customer.total_orders}</TableCell>
                  <TableCell className="text-right font-medium">
                    KES {customer.total_spent.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {format(new Date(customer.last_interaction), "MMM d, yyyy")}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewProfile(customer)}
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
