import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── Load Data ──────────────────────────────────────────────────────────────────
df = pd.read_excel('/mnt/user-data/outputs/pharma_sales_data.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M')
df['Year'] = df['Date'].dt.year
df['Month_Name'] = df['Date'].dt.strftime('%b %Y')

print("=" * 60)
print("PHARMACEUTICAL SALES DATA ANALYSIS")
print("=" * 60)

# ── 1. Basic EDA ───────────────────────────────────────────────────────────────
print("\n── Dataset Overview ──")
print(f"Shape          : {df.shape}")
print(f"Date Range     : {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"Total Revenue  : ₹{df['Revenue_INR'].sum():,.0f}")
print(f"Total Units    : {df['Units_Sold'].sum():,}")
print(f"States         : {df['State'].nunique()} | Cities: {df['City'].nunique()}")
print(f"Products       : {df['Product'].nunique()} | Categories: {df['Category'].nunique()}")
print(f"\nNull Values:\n{df.isnull().sum()}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nDescriptive Stats:\n{df[['Units_Sold','Revenue_INR']].describe().round(2)}")

# ── 2. Aggregations ────────────────────────────────────────────────────────────
product_rev   = df.groupby('Product')['Revenue_INR'].sum().sort_values(ascending=False)
category_rev  = df.groupby('Category')['Revenue_INR'].sum().sort_values(ascending=False)
state_rev     = df.groupby('State')['Revenue_INR'].sum().sort_values(ascending=False)
city_rev      = df.groupby('City')['Revenue_INR'].sum().sort_values(ascending=False)
monthly_rev   = df.groupby('Month')['Revenue_INR'].sum()
yearly_rev    = df.groupby('Year')['Revenue_INR'].sum()
product_units = df.groupby('Product')['Units_Sold'].sum().sort_values(ascending=False)

print("\n── Top 5 Products by Revenue ──")
print(product_rev.head().apply(lambda x: f"₹{x:,.0f}"))
print("\n── Revenue by State ──")
print(state_rev.apply(lambda x: f"₹{x:,.0f}"))
print("\n── Revenue by Category ──")
print(category_rev.apply(lambda x: f"₹{x:,.0f}"))

# MoM Growth
monthly_df = monthly_rev.reset_index()
monthly_df.columns = ['Month','Revenue']
monthly_df['MoM_Growth_%'] = monthly_df['Revenue'].pct_change() * 100
print(f"\n── Month-over-Month Growth (last 6 months) ──")
print(monthly_df.tail(6)[['Month','Revenue','MoM_Growth_%']].to_string(index=False))

# YoY
yoy = yearly_rev.pct_change() * 100
print(f"\n── Year-over-Year Revenue ──")
for yr, rev in yearly_rev.items():
    g = yoy.get(yr, 0)
    print(f"  {yr}: ₹{rev:,.0f}  (YoY: {g:+.1f}%)" if g else f"  {yr}: ₹{rev:,.0f}")

# ── 3. PLOTS ───────────────────────────────────────────────────────────────────
DARK_BLUE   = '#1F4E79'
MID_BLUE    = '#2E75B6'
ACCENT      = '#F4A261'
LIGHT_GRAY  = '#F0F4F8'
GREEN       = '#2D9E6B'
RED         = '#E63946'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.facecolor': LIGHT_GRAY,
    'figure.facecolor': 'white',
    'axes.grid': True,
    'grid.color': 'white',
    'grid.linewidth': 1.2,
})

def fmt_cr(x, pos=None):
    return f'₹{x/1e7:.1f}Cr'

# ── Fig 1: Monthly Revenue Trend ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
months_list = [str(m) for m in monthly_df['Month']]
x = np.arange(len(months_list))
ax.fill_between(x, monthly_df['Revenue'], alpha=0.18, color=MID_BLUE)
ax.plot(x, monthly_df['Revenue'], color=MID_BLUE, linewidth=2.5, marker='o', markersize=4)
ax.set_xticks(x[::3])
ax.set_xticklabels([months_list[i] for i in range(0, len(months_list), 3)], rotation=30, ha='right', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_cr))
ax.set_title('Monthly Revenue Trend (Jan 2023 – Dec 2024)', fontsize=14, fontweight='bold', color=DARK_BLUE, pad=12)
ax.set_ylabel('Revenue (₹ Crore)', fontsize=10)
plt.tight_layout()
plt.savefig('/home/claude/fig1_monthly_trend.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 2: Top Products ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

colors = [DARK_BLUE if i == 0 else MID_BLUE for i in range(len(product_rev))]
bars = axes[0].barh(product_rev.index[::-1], product_rev.values[::-1], color=colors[::-1], height=0.6)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(fmt_cr))
for bar, val in zip(bars, product_rev.values[::-1]):
    axes[0].text(bar.get_width() + product_rev.max()*0.01, bar.get_y()+bar.get_height()/2,
                 f'₹{val/1e7:.1f}Cr', va='center', fontsize=8.5, color=DARK_BLUE, fontweight='bold')
axes[0].set_title('Revenue by Product', fontsize=13, fontweight='bold', color=DARK_BLUE)
axes[0].set_xlabel('Revenue (₹ Crore)', fontsize=9)

wedge_colors = [DARK_BLUE, MID_BLUE, ACCENT, GREEN, '#A8DADC']
wedges, texts, autotexts = axes[1].pie(
    category_rev.values, labels=category_rev.index,
    autopct='%1.1f%%', colors=wedge_colors,
    startangle=140, pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2)
)
for t in autotexts:
    t.set_fontsize(9); t.set_fontweight('bold')
axes[1].set_title('Revenue by Drug Category', fontsize=13, fontweight='bold', color=DARK_BLUE)
plt.tight_layout()
plt.savefig('/home/claude/fig2_product_category.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 3: City & State Performance ────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

top10_city = city_rev.head(10)
bar_colors = [DARK_BLUE if df[df['City']==c]['State'].iloc[0]=='Uttar Pradesh' else ACCENT for c in top10_city.index]
bars = axes[0].bar(top10_city.index, top10_city.values, color=bar_colors, width=0.6, edgecolor='white')
axes[0].set_xticklabels(top10_city.index, rotation=35, ha='right', fontsize=9)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_cr))
axes[0].set_title('Top 10 Cities by Revenue', fontsize=13, fontweight='bold', color=DARK_BLUE)
axes[0].set_ylabel('Revenue (₹ Crore)')
from matplotlib.patches import Patch
axes[0].legend(handles=[Patch(color=DARK_BLUE, label='Uttar Pradesh'), Patch(color=ACCENT, label='Uttarakhand')], fontsize=9)

state_data = df.groupby(['State','Year'])['Revenue_INR'].sum().unstack()
x2 = np.arange(len(state_data.index))
w = 0.35
axes[1].bar(x2 - w/2, state_data[2023], width=w, color=MID_BLUE, label='2023', edgecolor='white')
axes[1].bar(x2 + w/2, state_data[2024], width=w, color=ACCENT, label='2024', edgecolor='white')
axes[1].set_xticks(x2); axes[1].set_xticklabels(state_data.index, fontsize=10)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(fmt_cr))
axes[1].set_title('State Revenue: 2023 vs 2024', fontsize=13, fontweight='bold', color=DARK_BLUE)
axes[1].set_ylabel('Revenue (₹ Crore)'); axes[1].legend()
plt.tight_layout()
plt.savefig('/home/claude/fig3_city_state.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 4: Heatmap – City x Category ──────────────────────────────────────────
pivot = df.groupby(['City','Category'])['Revenue_INR'].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 7))
import matplotlib.colors as mcolors
cmap = plt.cm.Blues
im = ax.imshow(pivot.values / 1e6, cmap=cmap, aspect='auto')
ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns, fontsize=10, fontweight='bold')
ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index, fontsize=9)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j] / 1e6
        ax.text(j, i, f'₹{val:.1f}L', ha='center', va='center', fontsize=7.5,
                color='white' if val > pivot.values.max()/1e6 * 0.6 else DARK_BLUE)
plt.colorbar(im, ax=ax, label='Revenue (₹ Lakhs)')
ax.set_title('Revenue Heatmap: City × Drug Category', fontsize=14, fontweight='bold', color=DARK_BLUE, pad=15)
plt.tight_layout()
plt.savefig('/home/claude/fig4_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n✅ All 4 charts saved.")
