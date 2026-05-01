import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Bell, BellRing, TrendingDown, Mail, RefreshCw, Calendar } from "lucide-react";

interface AlertData {
  id: string;
  leadId: string;
  leadName: string;
  leadEmail: string;
  currentRate: string;
  newRate: string;
  monthlySavings: string;
  totalInterestSaved: string;
  breakEvenMonths: number;
  emailSent: boolean;
  createdAt: string;
}

interface AlertStats {
  totalAlerts: number;
  alertsToday: number;
  alertsThisWeek: number;
  emailsSent: number;
  averageSavings: number;
}

export function AlertsSection() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: alertStatsData, isLoading: statsLoading } = useQuery({
    queryKey: ["/api/alerts/stats"],
    queryFn: async () => {
      const response = await fetch("/api/alerts/stats");
      if (!response.ok) throw new Error("Failed to fetch alert stats");
      return response.json();
    },
    refetchInterval: 30000,
  });

  const { data: recentAlertsData, isLoading: alertsLoading } = useQuery({
    queryKey: ["/api/alerts/recent"],
    queryFn: async () => {
      const response = await fetch("/api/alerts/recent?limit=10");
      if (!response.ok) throw new Error("Failed to fetch recent alerts");
      return response.json();
    },
    refetchInterval: 30000,
  });

  const checkAlertsMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/alerts/check");
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["/api/alerts/stats"] });
      queryClient.invalidateQueries({ queryKey: ["/api/alerts/recent"] });
      toast({
        title: "Alert Check Complete",
        description: `Checked ${data.checked} leads. Triggered ${data.triggered} new alerts.`,
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to check alerts. Please try again.",
        variant: "destructive",
      });
    },
  });

  const stats: AlertStats = alertStatsData?.stats || {
    totalAlerts: 0,
    alertsToday: 0,
    alertsThisWeek: 0,
    emailsSent: 0,
    averageSavings: 0,
  };

  const alerts: AlertData[] = recentAlertsData?.alerts || [];

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Alerts</p>
                <p className="text-3xl font-bold mt-1" data-testid="alert-stat-total">
                  {stats.totalAlerts}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Bell className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Today</p>
                <p className="text-3xl font-bold mt-1" data-testid="alert-stat-today">
                  {stats.alertsToday}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Calendar className="w-6 h-6 text-accent" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-3xl font-bold mt-1" data-testid="alert-stat-week">
                  {stats.alertsThisWeek}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-secondary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Emails Sent</p>
                <p className="text-3xl font-bold mt-1" data-testid="alert-stat-emails">
                  {stats.emailsSent}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Mail className="w-6 h-6 text-accent" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Savings</p>
                <p className="text-3xl font-bold mt-1" data-testid="alert-stat-avg">
                  ${stats.averageSavings}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Manual Check Button */}
      <div className="flex justify-end">
        <Button
          onClick={() => checkAlertsMutation.mutate()}
          disabled={checkAlertsMutation.isPending}
          data-testid="button-check-alerts"
        >
          {checkAlertsMutation.isPending ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
              Checking...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Check Alerts Now
            </>
          )}
        </Button>
      </div>

      {/* Recent Alerts Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle>Recent Alerts</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Refinance opportunities sent to leads
              </p>
            </div>
            <Badge variant="outline" className="w-fit">
              <BellRing className="w-3 h-3 mr-1" />
              Auto-refreshes every 30s
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          {alertsLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
            </div>
          ) : alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bell className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Alerts Yet</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                When mortgage rates drop enough to meet a lead's savings goal, alerts will appear here.
                Click "Check Alerts Now" to manually trigger a check.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Lead</TableHead>
                  <TableHead>Rate Change</TableHead>
                  <TableHead>Monthly Savings</TableHead>
                  <TableHead>Total Saved</TableHead>
                  <TableHead>Break-Even</TableHead>
                  <TableHead>Email Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.map((alert: AlertData) => (
                  <TableRow key={alert.id} data-testid={`alert-row-${alert.id}`}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{alert.leadName}</div>
                        <div className="text-xs text-muted-foreground">{alert.leadEmail}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm">
                          <span className="text-muted-foreground">{alert.currentRate}%</span>
                          <span className="mx-1">→</span>
                          <span className="font-medium text-accent">{alert.newRate}%</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-accent">
                        ${alert.monthlySavings}/mo
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">${alert.totalInterestSaved}</div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{alert.breakEvenMonths} months</div>
                    </TableCell>
                    <TableCell>
                      {alert.emailSent ? (
                        <Badge variant="default" className="bg-accent">
                          <Mail className="w-3 h-3 mr-1" />
                          Sent
                        </Badge>
                      ) : (
                        <Badge variant="outline">Pending</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm">
                          {new Date(alert.createdAt).toLocaleDateString()}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(alert.createdAt).toLocaleTimeString()}
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
