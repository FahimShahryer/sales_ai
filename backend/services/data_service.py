"""
Data Service - Sales Data Loading and Management
Handles loading and basic querying of sales data
"""
import pandas as pd
from typing import Optional
from backend.config import settings


class DataService:
    """Service for loading and managing sales data"""

    def __init__(self):
        """Initialize data service and load sales data"""
        print("🔧 Initializing Data Service...")

        self.df: Optional[pd.DataFrame] = None
        self.load_data()

        print(f"✅ Data Service initialized - {len(self.df):,} transactions loaded")

    def load_data(self):
        """Load sales transactions data"""
        try:
            self.df = pd.read_csv(settings.SALES_DATA_PATH)

            # Convert date column to datetime
            if 'Date' in self.df.columns:
                self.df['Date'] = pd.to_datetime(self.df['Date'])

            print(f"   Loaded {len(self.df):,} transactions")
            print(f"   Date range: {self.df['Date'].min().date()} to {self.df['Date'].max().date()}")
            print(f"   Columns: {len(self.df.columns)}")

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise

    def get_dataframe(self) -> pd.DataFrame:
        """Get the sales data DataFrame"""
        return self.df.copy()

    def get_summary(self) -> dict:
        """Get summary statistics of the dataset"""
        return {
            "total_transactions": len(self.df),
            "date_range": {
                "start": self.df['Date'].min().isoformat(),
                "end": self.df['Date'].max().isoformat()
            },
            "total_revenue": float(self.df['Net_Amount_BDT'].sum()),
            "total_profit": float(self.df['Profit_BDT'].sum()),
            "average_margin": float(self.df['Margin_Percent'].mean()),
            "divisions": self.df['Division_Name'].unique().tolist(),
            "branches": self.df['Branch_Name'].unique().tolist(),
        }

    def get_column_info(self) -> dict:
        """Get information about available columns"""
        return {
            "columns": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "sample_row": self.df.iloc[0].to_dict()
        }

    def validate_column(self, column_name: str) -> bool:
        """Check if a column exists in the dataset"""
        return column_name in self.df.columns

    def get_unique_values(self, column_name: str) -> list:
        """Get unique values for a categorical column"""
        if column_name not in self.df.columns:
            return []
        return self.df[column_name].unique().tolist()
