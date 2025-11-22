import Link from "next/link";
import { LayoutDashboard, MessageSquare, Package, ShoppingBag, Users, Settings, LogOut } from "lucide-react";

const navItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/" },
  { icon: MessageSquare, label: "Conversations", href: "/conversations" },
  { icon: Package, label: "Products", href: "/products" },
  { icon: ShoppingBag, label: "Orders", href: "/orders" },
  { icon: Users, label: "Customers", href: "/customers" },
  { icon: Settings, label: "Settings", href: "/settings" },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-0 flex flex-col">
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-xl font-bold text-blue-600 flex items-center gap-2">
          <span className="text-2xl">🛍️</span> Boutique AI
        </h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>
      
      <div className="p-4 border-t border-gray-100">
        <button className="flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg w-full transition-colors">
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
