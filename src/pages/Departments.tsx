import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Departments() {
  // Mock data - replace with your API calls
  const departments = [
    {
      id: 1,
      name: "Engineering",
      head: "John Smith",
      employees: 45,
      description: "Software development and technical operations",
    },
    {
      id: 2,
      name: "Marketing",
      head: "Sarah Johnson",
      employees: 12,
      description: "Brand management and market research",
    },
    {
      id: 3,
      name: "Sales",
      head: "Mike Williams",
      employees: 28,
      description: "Business development and client relations",
    },
    {
      id: 4,
      name: "Human Resources",
      head: "Emily Davis",
      employees: 8,
      description: "Recruitment and employee management",
    },
    {
      id: 5,
      name: "Finance",
      head: "David Brown",
      employees: 15,
      description: "Financial planning and accounting",
    },
    {
      id: 6,
      name: "Operations",
      head: "Lisa Anderson",
      employees: 22,
      description: "Business operations and logistics",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Departments</h1>
          <p className="text-muted-foreground mt-2">
            Manage organizational structure and department information
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Add Department
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {departments.map((dept) => (
          <Card
            key={dept.id}
            className="shadow-card hover:shadow-md transition-shadow cursor-pointer"
          >
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{dept.name}</span>
                <span className="text-sm font-normal text-muted-foreground">
                  {dept.employees} employees
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Department Head
                </p>
                <p className="text-base font-semibold mt-1">{dept.head}</p>
              </div>
              <p className="text-sm text-muted-foreground">
                {dept.description}
              </p>
              <Button variant="outline" className="w-full">
                View Details
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
