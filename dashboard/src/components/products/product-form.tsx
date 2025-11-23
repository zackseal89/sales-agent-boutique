"use client"

import { useState } from "react"
import { Product, createProduct, updateProduct } from "@/services/products"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

interface ProductFormProps {
  product?: Product | null
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function ProductForm({ product, open, onClose, onSuccess }: ProductFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: product?.name || "",
    price: product?.price || 0,
    description: product?.description || "",
    image_url: product?.image_url || "",
    stock_quantity: product?.stock_quantity || 0,
    category: product?.category || "",
    size: product?.size?.join(", ") || "",
    color: product?.color?.join(", ") || "",
    style: product?.style || "",
    season: product?.season || "",
    instagram_reference: product?.instagram_reference || "",
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)

    try {
      const productData = {
        ...formData,
        price: Number(formData.price),
        stock_quantity: Number(formData.stock_quantity),
        size: formData.size ? formData.size.split(",").map((s) => s.trim()) : undefined,
        color: formData.color ? formData.color.split(",").map((c) => c.trim()) : undefined,
      }

      if (product) {
        await updateProduct(product.id, productData)
      } else {
        await createProduct(productData)
      }

      onSuccess()
      onClose()
    } catch (error) {
      console.error("Failed to save product:", error)
      alert("Failed to save product")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{product ? "Edit Product" : "Add New Product"}</DialogTitle>
          <DialogDescription>
            {product ? "Update product details" : "Add a new product to your inventory"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Product Name *</Label>
              <Input
                id="name"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Input
                id="category"
                required
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="price">Price (KES) *</Label>
              <Input
                id="price"
                type="number"
                required
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="stock">Stock Quantity *</Label>
              <Input
                id="stock"
                type="number"
                required
                value={formData.stock_quantity}
                onChange={(e) => setFormData({ ...formData, stock_quantity: Number(e.target.value) })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="image_url">Image URL</Label>
            <Input
              id="image_url"
              type="url"
              value={formData.image_url}
              onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="size">Sizes (comma-separated)</Label>
              <Input
                id="size"
                placeholder="S, M, L, XL"
                value={formData.size}
                onChange={(e) => setFormData({ ...formData, size: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="color">Colors (comma-separated)</Label>
              <Input
                id="color"
                placeholder="Red, Blue, Black"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="style">Style</Label>
              <Input
                id="style"
                placeholder="Casual, Formal, etc."
                value={formData.style}
                onChange={(e) => setFormData({ ...formData, style: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="season">Season</Label>
              <Input
                id="season"
                placeholder="Summer, Winter, All Season"
                value={formData.season}
                onChange={(e) => setFormData({ ...formData, season: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="instagram">Instagram Reference</Label>
            <Input
              id="instagram"
              placeholder="@username/post123"
              value={formData.instagram_reference}
              onChange={(e) => setFormData({ ...formData, instagram_reference: e.target.value })}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : product ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
