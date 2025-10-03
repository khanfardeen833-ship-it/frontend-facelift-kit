import { Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Reports() {
  const reportTypes = [
    {
      id: 1,
      title: "Employee Attendance Report",
      description: "Detailed attendance records for all employees",
      icon: FileText,
    },
    {
      id: 2,
      title: "Leave Summary Report",
      description: "Comprehensive leave statistics and trends",
      icon: FileText,
    },
    {
      id: 3,
      title: "Department Performance",
      description: "Performance metrics by department",
      icon: FileText,
    },
    {
      id: 4,
      title: "Payroll Summary",
      description: "Salary and compensation breakdown",
      icon: FileText,
    },
    {
      id: 5,
      title: "Recruitment Report",
      description: "Hiring statistics and candidate pipeline",
      icon: FileText,
    },
    {
      id: 6,
      title: "Employee Turnover",
      description: "Retention and turnover analysis",
      icon: FileText,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground mt-2">
          Generate and export various HR reports
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {reportTypes.map((report) => (
          <Card
            key={report.id}
            className="shadow-card hover:shadow-md transition-shadow"
          >
            <CardHeader>
              <div className="flex items-start gap-4">
                <div className="bg-primary rounded-lg p-3">
                  <report.icon className="h-6 w-6 text-primary-foreground" />
                </div>
                <div className="flex-1">
                  <CardTitle className="text-lg">{report.title}</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {report.description}
              </p>
              <Button variant="outline" className="w-full gap-2">
                <Download className="h-4 w-4" />
                Generate Report
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
