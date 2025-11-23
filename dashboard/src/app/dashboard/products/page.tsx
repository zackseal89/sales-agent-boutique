"use client"

import { useState } from "react"
import { Product } from "@/services/products"
import { ProductsTable } from "@/components/products/products-table"
import { ProductForm } from "@/components/products/product-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ProductsPage() {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  function handleEdit(product: Product) {
    setSelectedProduct(product)
    setFormOpen(true)
  }

  function handleAdd() {
    setSelectedProduct(null)
    setFormOpen(true)
  }

  function handleFormClose() {
    setFormOpen(false)
    setSelectedProduct(null)
  }

  function handleFormSuccess() {
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <Card>
        <CardHeader>
          <CardTitle>Products Management</CardTitle>
          <CardDescription>
            Manage your fashion inventory. Add, edit, or remove products that the AI agent will recommend to customers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProductsTable
            key={refreshKey}
            onEdit={handleEdit}
            onAdd={handleAdd}
          />
        </CardContent>
      </Card>

      <ProductForm
        product={selectedProduct}
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
}
