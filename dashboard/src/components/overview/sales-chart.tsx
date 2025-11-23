"use client"

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const data = [
  { name: "Jan", total: 12400 },
  { name: "Feb", total: 15600 },
  { name: "Mar", total: 18900 },
  { name: "Apr", total: 16200 },
  { name: "May", total: 21500 },
  { name: "Jun", total: 19800 },
  { name: "Jul", total: 23400 },
  { name: "Aug", total: 25100 },
  { name: "Sep", total: 22800 },
  { name: "Oct", total: 27300 },
  { name: "Nov", total: 29600 },
  { name: "Dec", total: 31200 },
]

export function SalesChart() {
  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>Sales Overview</CardTitle>
        <CardDescription>Monthly revenue for 2024</CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data}>
            <XAxis
              dataKey="name"
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#888888"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `KES ${value / 1000}k`}
            />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="total"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
