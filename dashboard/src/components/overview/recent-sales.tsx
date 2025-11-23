import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

const recentSales = [
  {
    name: "Olivia Martin",
    email: "olivia.martin@email.com",
    amount: "+KES 1,999.00",
  },
  {
    name: "Jackson Lee",
    email: "jackson.lee@email.com",
    amount: "+KES 3,299.00",
  },
  {
    name: "Isabella Nguyen",
    email: "isabella.nguyen@email.com",
    amount: "+KES 2,499.00",
  },
  {
    name: "William Kim",
    email: "will@email.com",
    amount: "+KES 1,599.00",
  },
  {
    name: "Sofia Davis",
    email: "sofia.davis@email.com",
    amount: "+KES 4,299.00",
  },
]

export function RecentSales() {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Recent Sales</CardTitle>
        <CardDescription>You made 265 sales this month.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-8">
          {recentSales.map((sale, index) => (
            <div key={index} className="flex items-center">
              <Avatar className="h-9 w-9">
                <AvatarFallback>{sale.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
              </Avatar>
              <div className="ml-4 space-y-1">
                <p className="text-sm font-medium leading-none">{sale.name}</p>
                <p className="text-sm text-muted-foreground">{sale.email}</p>
              </div>
              <div className="ml-auto font-medium">{sale.amount}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
