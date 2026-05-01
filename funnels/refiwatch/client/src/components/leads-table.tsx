import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Eye, Mail, Trash2, Download, Filter } from "lucide-react";
import { Lead } from "@shared/schema";

export function LeadsTable() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("all");
  const limit = 10;

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: leadsData, isLoading } = useQuery({
    queryKey: ["/api/leads", page, search, statusFilter, dateFilter, limit],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...(search && { search }),
        ...(statusFilter && { status: statusFilter }),
        ...(dateFilter !== "all" && { dateFilter }),
      });
      
      const response = await fetch(`/api/leads?${params}`);
      if (!response.ok) throw new Error("Failed to fetch leads");
      return response.json();
    },
  });

  const { data: statsData } = useQuery({
    queryKey: ["/api/leads/stats"],
    queryFn: async () => {
      const response = await fetch("/api/leads/stats");
      if (!response.ok) throw new Error("Failed to fetch stats");
      return response.json();
    },
  });

  const deleteLeadMutation = useMutation({
    mutationFn: async (leadId: string) => {
      const response = await apiRequest("DELETE", `/api/leads/${leadId}`);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/leads"] });
      queryClient.invalidateQueries({ queryKey: ["/api/leads/stats"] });
      toast({
        title: "Lead deleted",
        description: "The lead has been successfully deleted.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to delete lead. Please try again.",
        variant: "destructive",
      });
    },
  });

  const exportLeads = () => {
    // TODO: Implement CSV export
    toast({
      title: "Export started",
      description: "Your CSV download will begin shortly.",
    });
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "active": return "default";
      case "contacted": return "secondary";
      case "new": return "default";
      case "closed": return "outline";
      default: return "outline";
    }
  };

  const stats = statsData?.stats || { total: 0, newToday: 0, thisWeek: 0, avgSavingsGoal: 0 };
  const leads = leadsData?.leads || [];
  const pagination = leadsData?.pagination || { total: 0, pages: 0 };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Leads</p>
                <p className="text-3xl font-bold mt-1" data-testid="stat-total">{stats.total}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Eye className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">New Today</p>
                <p className="text-3xl font-bold mt-1" data-testid="stat-today">{stats.newToday}</p>
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
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-3xl font-bold mt-1" data-testid="stat-week">{stats.thisWeek}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                <Filter className="w-6 h-6 text-secondary" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Savings Goal</p>
                <p className="text-3xl font-bold mt-1" data-testid="stat-avg">${stats.avgSavingsGoal}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Download className="w-6 h-6 text-accent" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Leads Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle>Lead Submissions</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">Manage and track all rate watch leads</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" data-testid="button-filter">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button onClick={exportLeads} size="sm" data-testid="button-export">
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
          
          {/* Search & Filters */}
          <div className="flex flex-col sm:flex-row gap-3 mt-4">
            <div className="flex-1 relative">
              <Input
                placeholder="Search leads by name, email, or phone..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
                data-testid="input-search"
              />
              <Eye className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            </div>
            <Select value={statusFilter || "all"} onValueChange={(val) => setStatusFilter(val === "all" ? "" : val)}>
              <SelectTrigger className="w-48" data-testid="select-status">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="contacted">Contacted</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={dateFilter} onValueChange={setDateFilter}>
              <SelectTrigger className="w-48" data-testid="select-date">
                <SelectValue placeholder="All Time" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Time</SelectItem>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Year Bought</TableHead>
                    <TableHead>Savings Goal</TableHead>
                    <TableHead>Current Rate</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Submitted</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leads.map((lead: Lead) => (
                    <TableRow key={lead.id} data-testid={`lead-row-${lead.id}`}>
                      <TableCell>
                        <div className="font-medium">{lead.name}</div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="text-sm">{lead.email}</div>
                          <div className="text-xs text-muted-foreground">{lead.phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>{lead.yearBought}</TableCell>
                      <TableCell className="font-medium">${lead.savingsGoal}/mo</TableCell>
                      <TableCell>{lead.currentRate || "—"}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(lead.status || "active")}>
                          {lead.status || "active"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="text-sm">{new Date(lead.createdAt).toLocaleDateString()}</div>
                          <div className="text-xs text-muted-foreground">{new Date(lead.createdAt).toLocaleTimeString()}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" data-testid={`button-view-${lead.id}`}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" asChild data-testid={`button-email-${lead.id}`}>
                            <a href={`mailto:${lead.email}`}>
                              <Mail className="w-4 h-4" />
                            </a>
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => deleteLeadMutation.mutate(lead.id)}
                            disabled={deleteLeadMutation.isPending}
                            data-testid={`button-delete-${lead.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-muted-foreground">
                  Showing <span className="font-medium">1-{Math.min(limit, leads.length)}</span> of <span className="font-medium">{pagination.total}</span> leads
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    data-testid="button-prev"
                  >
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" className="bg-primary text-primary-foreground">
                    {page}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
                    disabled={page >= pagination.pages}
                    data-testid="button-next"
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
