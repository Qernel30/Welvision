"""
Diagnosis Tab - Main Controller
Date & Time-Based Report Sheet with charts and export functionality
"""

import tkinter as tk

from frontend.utils.config import AppConfig
from ..utils.styles import Colors, Fonts
from ..utils.db_error_handler import DatabaseErrorHandler
from .report_data_table import ReportDataTable
from .control_panel import ControlPanel
from .action_panel import ActionPanel
from .status_chart import StatusChart
from .defectwise_chart import DefectwiseChart


class DiagnosisTab:
    """Diagnosis tab for generating and viewing reports with charts."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the diagnosis tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Components
        self.report_data_table = None
        self.control_panel = None
        self.action_panel = None
        self.status_chart = None
        self.defectwise_chart = None
        
        # Current report data
        self.current_data = []
        
    def setup(self):
        """Setup the diagnosis tab UI."""
        # Main container with dark blue background
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header frame for title and company info
        header_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        # Title (centered)
        title_label = tk.Label(
            header_frame,
            text="Date & Time-Based Report Sheet",
            font=Fonts.TITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack()
        
        # Company footer in top right
        company_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        company_frame.place(relx=1.0, y=10, anchor=tk.NE)
        
        company_label = tk.Label(
            company_frame,
            text="Developed and Maintained by\n© Welvision Pvt Limited",
            font=Fonts.TEXT_BOLD,
            fg="#FFFFFF",
            bg=Colors.PRIMARY_BG,
            justify=tk.RIGHT
        )
        company_label.pack(padx=20)
        
        # Top section: Report Data Table + Controls + Actions (increased height for visibility)
        top_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG, height=280)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        top_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Report Data Table (left side)
        self.report_data_table = ReportDataTable(top_frame, self)
        self.report_data_table.create()
        
        # Right panel: Controls + Actions (fixed width for better control display)
        right_panel = tk.Frame(top_frame, bg=Colors.PRIMARY_BG, width=320)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)  # Maintain fixed width
        
        # Control Panel
        self.control_panel = ControlPanel(right_panel, self)
        self.control_panel.create()
        
        # Action Panel
        self.action_panel = ActionPanel(right_panel, self)
        self.action_panel.create()
        
        # Bottom section: Charts (side by side with more height)
        charts_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status Chart (left)
        self.status_chart = StatusChart(charts_frame, self)
        self.status_chart.create()
        
        # Defectwise Chart (right)
        self.defectwise_chart = DefectwiseChart(charts_frame, self)
        self.defectwise_chart.create()
    
    def generate_report(self):
        """Generate report based on selected filters."""
        if self.control_panel:
            filters = self.control_panel.get_filters()
            if filters:  # Only proceed if validation passed
                self._fetch_and_display_data(filters)
    
    def save_chart(self):
        """Save the current charts as images."""
        try:
            import os
            from tkinter import messagebox
            
            # Get filters
            filters = self.control_panel.get_filters()
            if not filters:  # Validation failed
                return
            component_type = filters['component_type']
            report_type = filters['report_type']
            from_date = filters['from_date']
            to_date = filters['to_date']
            
            username = os.getlogin()
            
            # Save Status Chart
            if self.status_chart and self.status_chart.figure:
                # Create directory path for Status Chart
                status_path = f"C:\\Users\\{username}\\Desktop\\Diagnosis\\Charts\\{component_type}\\{report_type}\\Status"
                os.makedirs(status_path, exist_ok=True)
                
                # Create filename
                status_filename = f"{component_type}_{report_type}_Status_{from_date}_{to_date}.png"
                status_filepath = os.path.join(status_path, status_filename)
                
                # Save the figure
                self.status_chart.figure.savefig(status_filepath, dpi=300, bbox_inches='tight')
            
            # Save Defectwise Chart
            if self.defectwise_chart and self.defectwise_chart.figure:
                # Create directory path for Defectwise Chart
                defectwise_path = f"C:\\Users\\{username}\\Desktop\\Diagnosis\\Charts\\{component_type}\\{report_type}\\Defectwise"
                os.makedirs(defectwise_path, exist_ok=True)
                
                # Create filename
                defectwise_filename = f"{component_type}_{report_type}_Defectwise_{from_date}_{to_date}.png"
                defectwise_filepath = os.path.join(defectwise_path, defectwise_filename)
                
                # Save the figure
                self.defectwise_chart.figure.savefig(defectwise_filepath, dpi=300, bbox_inches='tight')
            
            messagebox.showinfo(
                "Charts Saved", 
                f"Charts saved successfully:\n\n"
                f"Status Chart:\n{status_filepath}\n\n"
                f"Defectwise Chart:\n{defectwise_filepath}"
            )
            
        except Exception as e:
            print(f"❌ Error saving charts: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Save Error", f"Failed to save charts:\n{str(e)}")
    
    def export_to_excel(self):
        """Export report data to Excel file."""
        if not self.current_data:
            print("⚠️ No data to export")
            return
        
        try:
            import os
            import pandas as pd
            from tkinter import messagebox
            
            # Get filters
            filters = self.control_panel.get_filters()
            if not filters:  # Validation failed
                return
            
            component_type = filters['component_type']
            report_type = filters['report_type']
            from_date = filters['from_date']
            to_date = filters['to_date']
            
            # Create directory path
            username = os.getlogin()
            base_path = f"C:\\Users\\{username}\\Desktop\\Diagnosis\\Report\\{component_type}\\{report_type}"
            os.makedirs(base_path, exist_ok=True)
            
            # Create filename
            filename = f"{component_type}_{report_type}_{from_date}_{to_date}.xlsx"
            filepath = os.path.join(base_path, filename)
            
            # Convert data to DataFrame
            df = pd.DataFrame(self.current_data)
            
            # Calculate sum row for numeric columns
            sum_row = {}
            for col in df.columns:
                if col in ['S.No', 'Component Type', 'Employee ID', 'Report Date', 'Start Time', 'End Time', 'Acceptance Rate']:
                    sum_row[col] = 'Total' if col == 'S.No' else ''
                else:
                    # Sum numeric columns
                    try:
                        sum_row[col] = df[col].sum()
                    except:
                        sum_row[col] = ''
            
            # Add sum row to DataFrame
            df = pd.concat([df, pd.DataFrame([sum_row])], ignore_index=True)
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Report')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Report']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            messagebox.showinfo("Export Success", f"Report exported to:\n{filepath}")
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
    
    def _fetch_and_display_data(self, filters):
        """
        Fetch data from database and display in table and charts.
        
        Args:
            filters: Dictionary with report_type, component_type, from_date, to_date
        """
        try:
            import mysql.connector
            from datetime import datetime
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            
            report_type = filters['report_type']
            component_type = filters['component_type']  # "Small"
            from_date = filters['from_date']
            to_date = filters['to_date']
            
            all_data = []
            
            if report_type == 'BF':
                # Query BF table only
                query = """
                    SELECT 
                        roller_type, employee_id, report_date, start_time, end_time,
                        total_inspected, total_accepted, total_rejected,
                        total_rust, total_dent, total_damage, 
                        total_high_head, total_low_head, others
                    FROM bf_roller_tracking
                    WHERE roller_type = %s AND report_date BETWEEN %s AND %s
                    ORDER BY report_date DESC, start_time DESC
                """
                cursor.execute(query, (component_type, from_date, to_date))
                
                for row in cursor.fetchall():
                    comp_type, emp_id, rep_date, start, end, inspected, accepted, rejected, \
                    rust, dent, damage, high_head, low_head, others = row
                    
                    acc_rate = (accepted / inspected * 100) if inspected > 0 else 0
                    
                    all_data.append({
                        'Component Type': comp_type,
                        'Employee ID': emp_id,
                        'Report Date': rep_date.strftime('%Y-%m-%d'),
                        'Start Time': str(start),
                        'End Time': str(end),
                        'BF Inspected': inspected,
                        'BF Accepted': accepted,
                        'BF Rejected': rejected,
                        'Acceptance Rate': f"{acc_rate:.2f}%",
                        'Rust': rust,
                        'Damage': damage,
                        'Dent': dent,
                        'High Head': high_head,
                        'Down Head': low_head,
                        'Others': others
                    })
            
            elif report_type == 'OD':
                # Query OD table only
                query = """
                    SELECT 
                        roller_type, employee_id, report_date, start_time, end_time,
                        total_inspected, total_accepted, total_rejected,
                        total_rust, total_dent, total_damage,
                        total_damage_on_end, total_spherical, others
                    FROM od_roller_tracking
                    WHERE roller_type = %s AND report_date BETWEEN %s AND %s
                    ORDER BY report_date DESC, start_time DESC
                """
                cursor.execute(query, (component_type, from_date, to_date))
                
                for row in cursor.fetchall():
                    comp_type, emp_id, rep_date, start, end, inspected, accepted, rejected, \
                    rust, dent, damage, damage_on_end, spherical, others = row
                    
                    acc_rate = (accepted / inspected * 100) if inspected > 0 else 0
                    
                    all_data.append({
                        'Component Type': comp_type,
                        'Employee ID': emp_id,
                        'Report Date': rep_date.strftime('%Y-%m-%d'),
                        'Start Time': str(start),
                        'End Time': str(end),
                        'OD Inspected': inspected,
                        'OD Accepted': accepted,
                        'OD Rejected': rejected,
                        'Acceptance Rate': f"{acc_rate:.2f}%",
                        'Rust': rust,
                        'Damage': damage,
                        'Dent': dent,
                        'Damage on End': damage_on_end,
                        'Spherical Mark': spherical,
                        'Others': others
                    })
            
            else:  # Overall
                # Query both tables and combine
                bf_query = """
                    SELECT 
                        roller_type, employee_id, report_date, start_time, end_time,
                        total_inspected, total_accepted, total_rejected
                    FROM bf_roller_tracking
                    WHERE roller_type = %s AND report_date BETWEEN %s AND %s
                    ORDER BY report_date DESC, start_time DESC
                """
                cursor.execute(bf_query, (component_type, from_date, to_date))
                bf_rows = cursor.fetchall()
                
                od_query = """
                    SELECT 
                        roller_type, employee_id, report_date, start_time, end_time,
                        total_inspected, total_accepted, total_rejected
                    FROM od_roller_tracking
                    WHERE roller_type = %s AND report_date BETWEEN %s AND %s
                    ORDER BY report_date DESC, start_time DESC
                """
                cursor.execute(od_query, (component_type, from_date, to_date))
                od_rows = cursor.fetchall()
                
                # Create a dictionary to group by date and employee
                combined_data = {}
                
                for row in bf_rows:
                    comp_type, emp_id, rep_date, start, end, inspected, accepted, rejected = row
                    key = (emp_id, rep_date, start)
                    
                    if key not in combined_data:
                        combined_data[key] = {
                            'Component Type': comp_type,
                            'Employee ID': emp_id,
                            'Report Date': rep_date.strftime('%Y-%m-%d'),
                            'Start Time': str(start),
                            'End Time': str(end),
                            'BF Inspected': inspected,
                            'BF Accepted': accepted,
                            'BF Rejected': rejected,
                            'OD Inspected': 0,
                            'OD Accepted': 0,
                            'OD Rejected': 0
                        }
                    else:
                        combined_data[key]['BF Inspected'] = inspected
                        combined_data[key]['BF Accepted'] = accepted
                        combined_data[key]['BF Rejected'] = rejected
                
                for row in od_rows:
                    comp_type, emp_id, rep_date, start, end, inspected, accepted, rejected = row
                    key = (emp_id, rep_date, start)
                    
                    if key not in combined_data:
                        combined_data[key] = {
                            'Component Type': comp_type,
                            'Employee ID': emp_id,
                            'Report Date': rep_date.strftime('%Y-%m-%d'),
                            'Start Time': str(start),
                            'End Time': str(end),
                            'BF Inspected': 0,
                            'BF Accepted': 0,
                            'BF Rejected': 0,
                            'OD Inspected': inspected,
                            'OD Accepted': accepted,
                            'OD Rejected': rejected
                        }
                    else:
                        combined_data[key]['OD Inspected'] = inspected
                        combined_data[key]['OD Accepted'] = accepted
                        combined_data[key]['OD Rejected'] = rejected
                
                # Calculate overall values
                for key, data in combined_data.items():
                    data['Overall Inspected'] = data['BF Inspected']
                    data['Overall Accepted'] = data['OD Accepted']
                    data['Overall Rejected'] = data['BF Rejected'] + data['OD Rejected']
                    
                    acc_rate = (data['Overall Accepted'] / data['Overall Inspected'] * 100) if data['Overall Inspected'] > 0 else 0
                    data['Acceptance Rate'] = f"{acc_rate:.2f}%"
                    
                    all_data.append(data)
            
            cursor.close()
            connection.close()
            
            # Update table
            if self.report_data_table:
                self.report_data_table.update_data(all_data, report_type)
            
            # Update charts
            self._update_charts(all_data, report_type)
            
            self.current_data = all_data
            
        except Exception as e:
            print(f"❌ Error fetching report data: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, self.parent, "fetching report data")
    
    def _update_charts(self, data, report_type):
        """Update both charts with the report data based on report type."""
        # Always update charts, even if data is empty
        if report_type == 'BF':
            # Calculate BF statistics for status chart
            total_inspected = sum(row.get('BF Inspected', 0) for row in data) if data else 0
            total_accepted = sum(row.get('BF Accepted', 0) for row in data) if data else 0
            total_rejected = sum(row.get('BF Rejected', 0) for row in data) if data else 0
            
            status_data = {
                'BF Inspected': total_inspected,
                'BF Accepted': total_accepted,
                'BF Rejected': total_rejected
            }
            
            # Calculate defect statistics
            defect_data = {
                'Rust': sum(row.get('Rust', 0) for row in data) if data else 0,
                'Damage': sum(row.get('Damage', 0) for row in data) if data else 0,
                'Dent': sum(row.get('Dent', 0) for row in data) if data else 0,
                'High Head': sum(row.get('High Head', 0) for row in data) if data else 0,
                'Down Head': sum(row.get('Down Head', 0) for row in data) if data else 0,
                'Others': sum(row.get('Others', 0) for row in data) if data else 0
            }
            
        elif report_type == 'OD':
            # Calculate OD statistics for status chart
            total_inspected = sum(row.get('OD Inspected', 0) for row in data) if data else 0
            total_accepted = sum(row.get('OD Accepted', 0) for row in data) if data else 0
            total_rejected = sum(row.get('OD Rejected', 0) for row in data) if data else 0
            
            status_data = {
                'OD Inspected': total_inspected,
                'OD Accepted': total_accepted,
                'OD Rejected': total_rejected
            }
            
            # Calculate defect statistics
            defect_data = {
                'Rust': sum(row.get('Rust', 0) for row in data) if data else 0,
                'Damage': sum(row.get('Damage', 0) for row in data) if data else 0,
                'Dent': sum(row.get('Dent', 0) for row in data) if data else 0,
                'Damage on End': sum(row.get('Damage on End', 0) for row in data) if data else 0,
                'Spherical Mark': sum(row.get('Spherical Mark', 0) for row in data) if data else 0,
                'Others': sum(row.get('Others', 0) for row in data) if data else 0
            }
            
        else:  # Overall
            # Calculate overall statistics for status chart
            total_inspected = sum(row.get('Overall Inspected', 0) for row in data) if data else 0
            total_accepted = sum(row.get('Overall Accepted', 0) for row in data) if data else 0
            total_rejected = sum(row.get('Overall Rejected', 0) for row in data) if data else 0
            
            status_data = {
                'Overall Inspected': total_inspected,
                'Overall Accepted': total_accepted,
                'Overall Rejected': total_rejected
            }
            
            # Calculate component-wise statistics for defectwise chart
            defect_data = {
                'BF Inspected': sum(row.get('BF Inspected', 0) for row in data) if data else 0,
                'BF Accepted': sum(row.get('BF Accepted', 0) for row in data) if data else 0,
                'BF Rejected': sum(row.get('BF Rejected', 0) for row in data) if data else 0,
                'OD Inspected': sum(row.get('OD Inspected', 0) for row in data) if data else 0,
                'OD Accepted': sum(row.get('OD Accepted', 0) for row in data) if data else 0,
                'OD Rejected': sum(row.get('OD Rejected', 0) for row in data) if data else 0
            }
        
        # Update charts
        if self.status_chart:
            self.status_chart.update_chart(status_data, report_type)
        
        if self.defectwise_chart:
            self.defectwise_chart.update_chart(defect_data, report_type)
