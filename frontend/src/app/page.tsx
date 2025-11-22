import { ArrowUpRight, DollarSign, MessageSquare, ShoppingBag, Users } from "lucide-react";

const stats = [
  {
    label: "Total Revenue",
    value: "KES 45,200",
    change: "+12.5%",
    icon: DollarSign,
    color: "text-green-600",
    bg: "bg-green-100",
  },
  {
    label: "Active Conversations",
    value: "12",
    change: "+4",
    icon: MessageSquare,
    color: "text-blue-600",
    bg: "bg-blue-100",
  },
  {
    label: "Pending Orders",
    value: "5",
    change: "-2",
    icon: ShoppingBag,
    color: "text-orange-600",
    bg: "bg-orange-100",
  },
  {
    label: "Total Customers",
    value: "148",
    change: "+8",
    icon: Users,
    color: "text-purple-600",
    bg: "bg-purple-100",
  },
];

const recentActivity = [
  {
    id: 1,
    user: "Sarah M.",
    action: "placed an order",
    details: "Blue Floral Dress (M)",
    time: "2 min ago",
    amount: "KES 2,500",
  },
  {
    id: 2,
    user: "John D.",
    action: "asked about",
    details: "Leather Jacket availability",
    time: "15 min ago",
    amount: null,
  },
  {
    id: 3,
    user: "Alice K.",
    action: "completed payment",
    details: "Order #1234",
    time: "1 hour ago",
    amount: "KES 4,000",
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 mt-1">Welcome back, here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <span className="flex items-center text-sm font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">
                {stat.change} <ArrowUpRight className="w-3 h-3 ml-1" />
              </span>
            </div>
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-500">{stat.label}</h3>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart Area (Placeholder) */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-gray-200 shadow-sm min-h-[400px]">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Revenue Overview</h3>
          <div className="h-80 bg-gray-50 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-200">
            <p className="text-gray-400">Chart Component Placeholder</p>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Recent Activity</h3>
          <div className="space-y-6">
            {recentActivity.map((item) => (
              <div key={item.id} className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs shrink-0">
                  {item.user.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {item.user} <span className="text-gray-500 font-normal">{item.action}</span>
                  </p>
                  <p className="text-sm text-gray-600 truncate">{item.details}</p>
                  <p className="text-xs text-gray-400 mt-1">{item.time}</p>
                </div>
                {item.amount && (
                  <span className="text-sm font-medium text-gray-900">{item.amount}</span>
                )}
              </div>
            ))}
          </div>
          <button className="w-full mt-6 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
            View All Activity
          </button>
        </div>
      </div>
    </div>
  );
}
