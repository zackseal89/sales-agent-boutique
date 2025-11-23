import { AnalyticsCards } from "@/components/overview/analytics-cards"
import { SalesChart } from "@/components/overview/sales-chart"
import { RecentSales } from "@/components/overview/recent-sales"

export default function OverviewPage() {
  return (
    <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <AnalyticsCards />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <SalesChart />
        <RecentSales />
      </div>
    </div>
  )
}
