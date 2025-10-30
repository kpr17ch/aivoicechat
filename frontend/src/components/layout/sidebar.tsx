'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Bot, BarChart3, Phone, Settings, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const navigation = [
  {
    name: 'Assistant',
    href: '/assistant',
    icon: Bot,
    active: true,
  },
  {
    name: 'Telefonnummern',
    href: '/phone-numbers',
    icon: Phone,
    active: false,
    disabled: true,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    active: false,
    disabled: true,
  },
  {
    name: 'Einstellungen',
    href: '/settings',
    icon: Settings,
    active: false,
    disabled: true,
  },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full w-64 border-r bg-background transition-transform duration-200 md:sticky md:top-14 md:z-30 md:h-[calc(100vh-3.5rem)] md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-14 items-center justify-between border-b px-4 md:hidden">
          <span className="font-semibold">Menu</span>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="space-y-1 p-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.disabled ? '#' : item.href}
                onClick={(e) => {
                  if (item.disabled) {
                    e.preventDefault();
                  } else if (onClose) {
                    onClose();
                  }
                }}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : item.disabled
                    ? 'text-muted-foreground cursor-not-allowed opacity-60'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
                {item.disabled && (
                  <span className="ml-auto text-xs bg-muted px-2 py-0.5 rounded">
                    Bald
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t p-4">
          <div className="text-xs text-muted-foreground">
            <p className="font-medium mb-1">Telo AI Platform</p>
            <p>Version 1.0.0</p>
          </div>
        </div>
      </aside>
    </>
  );
}
