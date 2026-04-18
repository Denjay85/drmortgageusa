import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { LeadsTable } from "@/components/leads-table";
import { AlertsSection } from "@/components/alerts-section";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Users, Bell, Lock, LogOut } from "lucide-react";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

function AdminLogin({ onLogin }: { onLogin: () => void }) {
  const [password, setPassword] = useState("");
  const { toast } = useToast();

  const loginMutation = useMutation({
    mutationFn: async (password: string) => {
      const response = await apiRequest("POST", "/api/admin/login", { password });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Welcome back!",
        description: "You are now logged in to the admin dashboard.",
      });
      onLogin();
    },
    onError: (error: any) => {
      toast({
        title: "Login failed",
        description: error.message || "Invalid password. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(password);
  };

  return (
    <div className="min-h-screen flex flex-col bg-muted">
      <SiteHeader />
      
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-lg border border-border p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lock className="w-8 h-8 text-primary" />
              </div>
              <h1 className="text-2xl font-bold">Admin Login</h1>
              <p className="text-muted-foreground mt-2">Enter your password to access the dashboard</p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter admin password"
                  className="mt-1.5"
                  data-testid="input-admin-password"
                  autoFocus
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full"
                disabled={loginMutation.isPending || !password}
                data-testid="button-admin-login"
              >
                {loginMutation.isPending ? "Logging in..." : "Log in"}
              </Button>
            </form>
          </div>
        </div>
      </main>
      
      <SiteFooter />
    </div>
  );
}

function AdminDashboard() {
  const { toast } = useToast();

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/admin/logout", {});
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/session"] });
      toast({
        title: "Logged out",
        description: "You have been logged out successfully.",
      });
    },
  });

  return (
    <div className="min-h-screen flex flex-col bg-muted">
      <SiteHeader />
      
      <main className="flex-1 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl font-bold">Admin Dashboard</h2>
            <p className="text-muted-foreground mt-1">Manage leads and monitor refinance alerts</p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => logoutMutation.mutate()}
            disabled={logoutMutation.isPending}
            data-testid="button-admin-logout"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Log out
          </Button>
        </div>
        
        <Tabs defaultValue="leads" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2" data-testid="admin-tabs">
            <TabsTrigger value="leads" data-testid="tab-leads">
              <Users className="w-4 h-4 mr-2" />
              Leads
            </TabsTrigger>
            <TabsTrigger value="alerts" data-testid="tab-alerts">
              <Bell className="w-4 h-4 mr-2" />
              Alerts
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="leads" className="space-y-6">
            <LeadsTable />
          </TabsContent>
          
          <TabsContent value="alerts" className="space-y-6">
            <AlertsSection />
          </TabsContent>
        </Tabs>
      </main>
      
      <SiteFooter />
    </div>
  );
}

export default function Admin() {
  const { data, isLoading } = useQuery<{ authenticated: boolean }>({
    queryKey: ["/api/admin/session"],
  });

  const handleLogin = () => {
    queryClient.invalidateQueries({ queryKey: ["/api/admin/session"] });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!data?.authenticated) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return <AdminDashboard />;
}
