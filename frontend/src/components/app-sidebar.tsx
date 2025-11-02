'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { Bot, Phone, BarChart3, Settings, User, Home, MessageSquareText } from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const navigation = [
  {
    name: 'Startseite',
    href: '/',
    icon: Home,
    disabled: false,
  },
  {
    name: 'Assistant',
    href: '/assistant',
    icon: Bot,
    disabled: false,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    disabled: false,
  },
  {
    name: 'Gespräche',
    href: '/analytics/conversations',
    icon: MessageSquareText,
    disabled: false,
  },
  {
    name: 'Telefonnummern',
    href: '/phone-numbers',
    icon: Phone,
    disabled: true,
  },
  {
    name: 'Einstellungen',
    href: '/settings',
    icon: Settings,
    disabled: true,
  },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-black/15 p-4">
        <div className="flex items-center">
          <Image
            src="/logo.png"
            alt="Telo AI Logo"
            width={155}
            height={50}
            priority
            className="h-10 w-auto"
          />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;

                return (
                  <SidebarMenuItem key={item.name}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      disabled={item.disabled}
                      tooltip={item.name}
                    >
                      <Link href={item.disabled ? '#' : item.href}>
                        <Icon className="h-5 w-5" />
                        <span>{item.name}</span>
                        {item.disabled && (
                          <span className="ml-auto text-xs bg-muted px-2 py-0.5 rounded">
                            Bald
                          </span>
                        )}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <User className="h-5 w-5" />
                  <span>demo@telo.ai</span>
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent side="top" align="start" className="w-[--radix-popper-anchor-width]">
                <DropdownMenuItem disabled>
                  <Settings className="h-4 w-4 mr-2" />
                  Einstellungen
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled>
                  Abmelden
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
